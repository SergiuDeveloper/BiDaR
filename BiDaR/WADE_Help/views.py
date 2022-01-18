from datetime import datetime

from django.contrib import messages
from django.http import JsonResponse, HttpResponseServerError, Http404, HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView, ListView, FormView, TemplateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, ProtectedError, RestrictedError
from django.utils.decorators import method_decorator
from django.conf import settings
from django.template.loader import render_to_string
from wkhtmltopdf.views import PDFTemplateResponse

from .decorators import mentoring_program_is_not_deleted, survey_progress_program_is_not_deleted, mentoring_program_is_available
from .forms import AddMentoringProgramForm, AnswerSurveyForm, DeleteMentoringProgramForm, InterruptMentoringProgramForm
from .custom_filters.dashboard_filter import DashboardFilter, DashboardSliceFilter
from .models import MentoringProgram, SurveyProgress, SurveyTemplate
from .services import mentoringProgramService, processService, milestoneTemplateService, questionsService, surveyService, answerService, milestoneProgressService, \
    surveyProgressService, paginationBarService, statusUpdateService, mentoringProgramReportService, dashboardService, dashboardSliceService, dbExportService
from utils.enums import PermissionErrorMessages, SurveyErrorMessages, SubmitMessages, AccessLevel, SubmitErrorMessages
from utils.constants import AUTOCOMPLETE_DROPDOWN_LINES, SUPERVISOR_OVERDUE_DATE_DAYS_DELAY, MENTORING_PROGRAM_STATUSES, SURVEY_TEMPLATE_TARGETS, \
    SURVEY_PROGRESS_STATUSES, ANSWER_TEXT_MAX_LENGTH
from utils.methods import get_url_last_section
from accounts.services import userProfileServices, userServices, emailSenderService
from accounts.decorators import user_is_creator_on_not_default, user_has_view_programs_rights, user_has_supervisor_rights, request_is_ajax, get_request_is_ajax, \
    user_has_delete_programs_rights
from accounts.middlewares.user_middlewares import LoggedUserProfile
from accounts.utils.methods import normalize_user_info


def get_questions_and_answers(question_groups, progress=0):
    questions_info = []
    for group in question_groups:
        questions = questionsService.get_survey_questions({'group': group}).order_by('order_number')
        answer_templates = questionsService.get_question_answer_templates({'question_group': group})
        questions_n_answers = []
        for question in questions:
            answers = []
            if progress != 0:
                answers = questionsService.get_question_answers({'question_template': question, 'survey_progress': progress})
            questions_n_answers.append({"question": question, "answers": answers})
        info = {
            "group_info": group,
            "answer_templates": answer_templates,
            "qna": questions_n_answers,
        }
        questions_info.append(info)
    return questions_info


@method_decorator(user_has_view_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(mentoring_program_is_not_deleted('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
class MentoringProgramDV(DetailView):
    template_name = "surveys/program_view.html"
    context_object_name = 'mentoring_program_details'
    model = MentoringProgram
    pk_url_kwarg = 'mentoring_program_id'

    def get_context_data(self, **kwargs):
        context = super(MentoringProgramDV, self).get_context_data(**kwargs)
        process = milestoneProgressService.get_milestone_progress({'mentoring_program': self.kwargs["mentoring_program_id"]})[0].milestone_template.process
        context['process_category'] = process.process_category
        context['process'] = process.name
        context['milestone_progress_list'] = mentoringProgramService.get_mentoring_program_milestones({'mentoring_program': self.kwargs["mentoring_program_id"]})
        # TODO: delete after a better solution is implemented
        mentoring_program = self.get_object()
        context['edit_allowed'] = mentoring_program.status not in [MENTORING_PROGRAM_STATUSES['interrupted'], MENTORING_PROGRAM_STATUSES['deleted']] and \
                                  (mentoring_program.supervisor.user == self.request.user or
                                   mentoring_program.supervisor.hierarchy_id.startswith(f'{self.request.user.userprofile.hierarchy_id}-'))
        return context


@method_decorator(user_has_supervisor_rights, name='dispatch')
class MentoringProgramLV(LoggedUserProfile, ListView):
    template_name = "surveys/mentoring_programs.html"
    default_page_size = 5

    def get_queryset(self):
        search_text = self.get_search_text()
        ordering = self.get_ordering()
        return mentoringProgramService.get_mentoring_programs_for_pagination(self.user_profile, search_text, ordering)

    def get_search_text(self):
        search_text = self.request.GET.get('search_text')
        return search_text

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        return ordering

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')
        if page_size and isinstance(page_size, str) and not page_size.isdigit():
            page_size = self.default_page_size
        return page_size or self.default_page_size

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_text'] = self.get_search_text()
        context['ordering'] = self.get_ordering()
        context['pagination_buttons'] = paginationBarService.get_pagination_buttons(context['paginator'].num_pages, context['page_obj'].number)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('api'):
            response = render(self.request, 'surveys/table_snippets/mentoring_programs_table.html', context, content_type='application/xhtml+xml')
            return response
        else:
            return super().render_to_response(context, **response_kwargs)


@method_decorator(user_has_delete_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(user_has_view_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(mentoring_program_is_available('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(get_request_is_ajax, name="dispatch")
class MentoringProgramSimpleDelV(DeleteView):
    http_method_names = ['get', 'post']
    template_name = 'surveys/mentoring_program_snippets/mentoring_program_delete_form.html'
    model = MentoringProgram
    pk_url_kwarg = 'mentoring_program_id'
    context_object_name = 'mentoring_program'
    success_url = reverse_lazy('surveys:mentoring_programs')

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return JsonResponse({'html_form': render_to_string(self.template_name, self.get_context_data(), request=request)})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, SubmitMessages.MENTORING_PROGRAM_SIMPLE_DELETE.value['submit_message'])
        except (ProtectedError, RestrictedError):
            messages.error(request, SubmitErrorMessages.MENTORING_PROGRAM_SIMPLE_DELETE.value['submit_message'])
        return redirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        mentoring_program = self.get_object()
        if mentoring_program:
            if mentoringProgramService.check_program_contains_answered_surveys(mentoring_program):
                kwargs['mentoring_program'] = mentoring_program
                view = MentoringProgramDeleteFV.as_view()
                return view(request, *args, **kwargs)
            else:
                return super().dispatch(request, *args, **kwargs)


@method_decorator(mentoring_program_is_available('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
class MentoringProgramDeleteFV(FormView):
    http_method_names = ['get', 'post']
    form_class = DeleteMentoringProgramForm
    template_name = 'surveys/mentoring_program_snippets/mentoring_program_delete_form.html'
    success_url = reverse_lazy('surveys:mentoring_programs')

    def get(self, request, *args, **kwargs):
        return JsonResponse({'html_form': render_to_string(self.template_name, self.get_context_data(), request=request)})

    def form_valid(self, form):
        messages.success(self.request, SubmitMessages.MENTORING_PROGRAM_DELETE.value['submit_message'])
        if settings.SENDING_EMAILS_ALLOWED:
            emailSenderService.send_email_for_mentoring_program_delete(normalize_user_info(userProfileServices.get_user_profile_by_user_id(self.request.user.id)),
                                                                       self.kwargs['mentoring_program_id'], form.cleaned_data['delete_reason'])
        return super(MentoringProgramDeleteFV, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, SubmitErrorMessages.MENTORING_PROGRAM_DELETE.value['submit_message'])
        return super(MentoringProgramDeleteFV, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['mentoring_program'] = self.kwargs['mentoring_program']
        context['program_contains_answers'] = True
        return context


@method_decorator(user_has_delete_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(user_has_view_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(mentoring_program_is_available('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(request_is_ajax, name="dispatch")
class MentoringProgramEditTV(TemplateView):
    http_method_names = ['get']
    template_name = 'surveys/mentoring_program_snippets/mentoring_program_edit.html'


@method_decorator(user_has_delete_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(user_has_view_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(mentoring_program_is_available('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(get_request_is_ajax, name="dispatch")
class MentoringProgramInterruptUV(UpdateView):
    template_name = 'surveys/mentoring_program_snippets/mentoring_program_interrupt_form.html'
    form_class = InterruptMentoringProgramForm
    model = MentoringProgram
    pk_url_kwarg = 'mentoring_program_id'
    context_object_name = 'mentoring_program'
    success_url = reverse_lazy('surveys:mentoring_programs')

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return JsonResponse({'html_form': render_to_string(self.template_name, self.get_context_data(), request=request)})

    def form_valid(self, form):
        mentoringProgramService.interrupt_mentoring_program(form)
        messages.success(self.request, SubmitMessages.MENTORING_PROGRAM_INTERRUPT.value['submit_message'])
        return super(MentoringProgramInterruptUV, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, SubmitErrorMessages.MENTORING_PROGRAM_INTERRUPT.value['submit_message'])
        return super(MentoringProgramInterruptUV, self).form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        mentoring_program = self.get_object()
        if mentoring_program:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()


@method_decorator(user_has_supervisor_rights, name='dispatch')
class SurveyListLV(LoggedUserProfile, ListView):
    template_name = "surveys/surveys.html"
    default_page_size = 8

    def get_queryset(self):
        search_text = self.get_search_text()
        ordering = self.get_ordering()
        return surveyService.get_survey_templates_with_defaults(self.user_profile, search_text, ordering)

    def get_search_text(self):
        search_text = self.request.GET.get('search_text')
        return search_text

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        return ordering

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')
        if page_size and isinstance(page_size, str) and not page_size.isdigit():
            page_size = self.default_page_size
        return page_size or self.default_page_size

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_text'] = self.get_search_text()
        context['ordering'] = self.get_ordering()
        context['pagination_buttons'] = paginationBarService.get_pagination_buttons(context['paginator'].num_pages, context['page_obj'].number)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('api'):
            response = render(self.request, 'surveys/table_snippets/surveys_table.html', context, content_type='application/xhtml+xml')
            return response
        else:
            return super().render_to_response(context, **response_kwargs)


@method_decorator(user_is_creator_on_not_default('survey_id', surveyService.get_single_survey_template), name="dispatch")
@method_decorator(user_has_supervisor_rights, name='dispatch')
class ConfigSurveyDV(DetailView):
    template_name = "surveys/view_survey.html"
    context_object_name = 'survey_info'
    pk_url_kwarg = 'survey_id'
    model = SurveyTemplate

    def get_context_data(self, **kwargs):
        context = super(ConfigSurveyDV, self).get_context_data(**kwargs)
        groups = questionsService.get_question_groups({"survey": self.kwargs['survey_id']}).order_by('order_number')
        context['questions_info'] = get_questions_and_answers(groups)
        context['textarea_maxlength'] = ANSWER_TEXT_MAX_LENGTH

        return context


class AnswerSurveyFV(SingleObjectMixin, FormView):
    form_class = AnswerSurveyForm

    def post(self, request, *args, **kwargs):
        survey_progress = surveyProgressService.get_single_survey_progress({'id': self.kwargs['survey_progress_id']})

        if not questionsService.check_if_mandatory_questions_answered(survey_progress, request.POST):
            return render(request, 'mentorship/errors/error.html', SurveyErrorMessages.NOT_ANSWERED.value)

        answers = answerService.get_answers_for_questions_from_post_data(request.POST)

        for key, value in answers.items():
            for answer in value:
                question_template = questionsService.get_single_question_template({'id': key})
                if question_template:
                    answerService.answer_question({'survey_progress': survey_progress,
                                                   'question_template': question_template,
                                                   'answer_text': answer[:ANSWER_TEXT_MAX_LENGTH + 1]})
                else:
                    return HttpResponseServerError()
        updated_survey_progress = statusUpdateService.answer_survey(survey_progress)
        updated_supervisor_survey_progress = statusUpdateService.verify_supervisor_survey_status(updated_survey_progress)

        if settings.SENDING_EMAILS_ALLOWED:
            if updated_supervisor_survey_progress:
                mentee_survey_progress = surveyProgressService.get_single_survey_progress({'milestone_progress': survey_progress.milestone_progress,
                                                                                           'survey_template__target': SURVEY_TEMPLATE_TARGETS['mentee']})
                mentor_survey_progress = surveyProgressService.get_single_survey_progress({'milestone_progress': survey_progress.milestone_progress,
                                                                                           'survey_template__target': SURVEY_TEMPLATE_TARGETS['mentor']})
                emailSenderService.send_email_for_assignment_to_survey(updated_supervisor_survey_progress,
                                                                       updated_supervisor_survey_progress.milestone_progress.milestone_template.process.process_category,
                                                                       mentee_survey_progress, mentor_survey_progress)

        return render(request, 'mentorship/submit_message.html', SubmitMessages.SURVEY.value)


class AnswerSurveyDV(DetailView):
    template_name = "surveys/answer_survey.html"
    context_object_name = 'survey'
    pk_url_kwarg = 'survey_progress_id'
    model = SurveyProgress

    def get_context_data(self, **kwargs):
        context = super(AnswerSurveyDV, self).get_context_data(**kwargs)
        groups = questionsService.get_question_groups({"survey": context['survey'].survey_template.id}).order_by('order_number')
        context['questions_info'] = get_questions_and_answers(groups)
        context['textarea_maxlength'] = ANSWER_TEXT_MAX_LENGTH
        context['subjects'] = surveyProgressService.get_survey_progress_subjects(context['survey'])
        return context


@method_decorator(survey_progress_program_is_not_deleted('survey_progress_id', surveyProgressService.get_single_survey_progress), name="dispatch")
class AnswerSurvey(View):
    def get(self, request, *args, **kwargs):
        view = AnswerSurveyDV.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = AnswerSurveyFV.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        survey_progress = surveyProgressService.get_single_survey_progress({'id': self.kwargs['survey_progress_id']})
        if not survey_progress:
            return super().dispatch(request, *args, **kwargs)

        user_profile = userProfileServices.get_user_profile_by_user_id(request.user.id)
        if user_profile != survey_progress.user:
            return render(request, 'mentorship/errors/error.html', PermissionErrorMessages.NOT_AUTHORIZED.value)
        elif survey_progress.status == SURVEY_PROGRESS_STATUSES['complete']:
            return redirect(to='surveys:view_answers', survey_progress_id=self.kwargs['survey_progress_id'])
        elif survey_progress.status == SURVEY_PROGRESS_STATUSES['overdue']:
            return render(request, 'mentorship/errors/error.html', SurveyErrorMessages.OVERDUE.value)
        elif survey_progress.status == SURVEY_PROGRESS_STATUSES['interrupted']:
            return render(request, 'mentorship/errors/error.html', SurveyErrorMessages.INTERRUPTED.value)
        elif survey_progress.status == SURVEY_PROGRESS_STATUSES['skipped']:
            return render(request, 'mentorship/errors/error.html', SurveyErrorMessages.SKIPPED.value)
        elif survey_progress.status == SURVEY_PROGRESS_STATUSES['not_assigned']:
            return render(request, 'mentorship/errors/error.html', SurveyErrorMessages.NOT_ASSIGNED.value)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(survey_progress_program_is_not_deleted('survey_progress_id', surveyProgressService.get_single_survey_progress), name="dispatch")
@method_decorator(user_has_view_programs_rights('survey_progress_id', surveyProgressService.get_single_survey_progress), name="dispatch")
class ViewAnswersDV(DetailView):
    template_name = "surveys/view_answers.html"
    context_object_name = 'survey_progress'
    pk_url_kwarg = 'survey_progress_id'
    model = SurveyProgress

    def get_context_data(self, **kwargs):
        progress = surveyProgressService.get_single_survey_progress({"id": self.kwargs['survey_progress_id']})
        context = super(ViewAnswersDV, self).get_context_data(**kwargs)
        q_group = questionsService.get_question_groups({"survey": progress.survey_template})
        context['questions_info'] = get_questions_and_answers(q_group, progress)
        context['textarea_maxlength'] = ANSWER_TEXT_MAX_LENGTH
        return context


@method_decorator(user_has_supervisor_rights, name='dispatch')
class MentoringProgramFV(FormView):
    template_name = 'surveys/add_mentoring_program.html'
    form_class = AddMentoringProgramForm
    model = MentoringProgram

    def get_context_data(self, *args, **kwargs):
        context = super(MentoringProgramFV, self).get_context_data(**kwargs)
        processes = processService.get_default_processes()
        context['processes'] = processes
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.data['process'] or form.data['process'] == '':
            form.add_error(None, 'No process selected')
            return self.form_invalid(form)
        if form.is_valid():
            process = processService.get_single_process({'id': form.data['process']})
            mentoring_program = mentoringProgramService.save_mentoring_program_form(form, request.user.username)
            milestone_progress_list = milestoneProgressService.create_milestone_progress_for_mentoring_program(mentoring_program, form.data['process'],
                                                                                                               form.cleaned_data['start_date'])
            survey_progress_list = surveyProgressService.create_survey_progresses_for_milestone_progress_list(milestone_progress_list, mentoring_program)
            if settings.SENDING_EMAILS_ALLOWED:
                emailSenderService.send_email_for_program_created(mentoring_program, process.process_category)
                if mentoring_program.status == MENTORING_PROGRAM_STATUSES['active']:
                    emailSenderService.send_email_for_welcome_to_program(mentoring_program, process.process_category)
                    if survey_progress_list:
                        for survey_progress in survey_progress_list:
                            if survey_progress.status == SURVEY_PROGRESS_STATUSES['assigned'] or survey_progress.status == SURVEY_PROGRESS_STATUSES['late']:
                                if survey_progress.survey_template.target == SURVEY_TEMPLATE_TARGETS['supervisor']:
                                    mentee_survey_progress = surveyProgressService.get_single_survey_progress({'milestone_progress': survey_progress.milestone_progress,
                                                                                                               'survey_template__target': SURVEY_TEMPLATE_TARGETS['mentee']})
                                    mentor_survey_progress = surveyProgressService.get_single_survey_progress({'milestone_progress': survey_progress.milestone_progress,
                                                                                                               'survey_template__target': SURVEY_TEMPLATE_TARGETS['mentor']})
                                    emailSenderService.send_email_for_assignment_to_survey(survey_progress, process.process_category, mentee_survey_progress, mentor_survey_progress)
                                else:
                                    emailSenderService.send_email_for_assignment_to_survey(survey_progress, process.process_category)

            messages.success(request, SubmitMessages.MENTORING_PROGRAM.value['submit_message'])
            return redirect(self.get_success_url())
        else:
            return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('surveys:mentoring_programs')


@method_decorator(user_has_supervisor_rights, name='dispatch')
class MentoringProcessesLV(LoggedUserProfile, ListView):
    template_name = 'surveys/mentoring_processes.html'
    default_page_size = 5

    def get_queryset(self):
        search_text = self.get_search_text()
        ordering = self.get_ordering()
        return processService.get_user_processes_with_defaults(self.user_profile, search_text, ordering)

    def get_search_text(self):
        search_text = self.request.GET.get('search_text')
        return search_text

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        return ordering

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')
        if page_size and isinstance(page_size, str) and not page_size.isdigit():
            page_size = self.default_page_size
        return page_size or self.default_page_size

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_text'] = self.get_search_text()
        context['ordering'] = self.get_ordering()
        context['pagination_buttons'] = paginationBarService.get_pagination_buttons(context['paginator'].num_pages, context['page_obj'].number)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('api'):
            response = render(self.request, 'surveys/table_snippets/mentoring_processes_table.html', context, content_type='application/xhtml+xml')
            return response
        else:
            return super().render_to_response(context, **response_kwargs)


@method_decorator(user_is_creator_on_not_default('process_id', processService.get_single_process), name="dispatch")
@method_decorator(user_has_supervisor_rights, name='dispatch')
class MentoringProcessDV(DetailView):
    template_name = "surveys/mentoring_process.html"
    context_object_name = 'process'
    pk_url_kwarg = 'process_id'

    def get_queryset(self):
        return processService.get_single_available_process({"id": self.kwargs['process_id']})

    def get_context_data(self, **kwargs):
        context = super(MentoringProcessDV, self).get_context_data(**kwargs)
        context['milestone_list'] = milestoneTemplateService.get_all_milestone_for_process({'process': self.kwargs['process_id']})
        return context


@method_decorator(user_has_supervisor_rights, name='dispatch')
class MilestoneForAProcess(ListView):
    template_name = 'surveys/html_snippets/process_milestones_for_add.html'
    context_object_name = 'milestones'
    content_type = 'application/xhtml+xml'
    http_method_names = ['get']

    def get_queryset(self):
        milestones = milestoneTemplateService.get_all_milestone_for_process({'process': self.request.GET.get('process_id')})
        return milestoneProgressService.build_milestone_progress(milestones, self.request.GET.get('date'))

    def get_context_data(self, **kwargs):
        context = super(MilestoneForAProcess, self).get_context_data(**kwargs)
        context['end_date_delay'] = SUPERVISOR_OVERDUE_DATE_DAYS_DELAY
        return context


@method_decorator(user_has_view_programs_rights('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
@method_decorator(mentoring_program_is_not_deleted('mentoring_program_id', mentoringProgramService.get_single_mentoring_program), name="dispatch")
class MentoringProgramReportDV(DetailView):
    context_object_name = 'program_information'
    model = MentoringProgram
    pk_url_kwarg = 'mentoring_program_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.download_request:
            context['PDF_STATIC_ROOT'] = fr'{settings.PDF_STATIC_ROOT}'
            context['STATIC_ROOT'] = fr'{settings.STATIC_ROOT}'
        milestones = milestoneProgressService.get_milestone_progress({"mentoring_program": context['program_information']})
        process = milestones[0].milestone_template.process
        context['process'] = process.name
        context['process_category'] = process.process_category
        context['program_interrupted'] = context[self.context_object_name].status == MENTORING_PROGRAM_STATUSES['interrupted']
        context['monitoring'] = mentoringProgramReportService.get_monitoring_statuses(milestones)
        context['evaluation'] = mentoringProgramReportService.get_evaluation_data(milestones)
        context['suggestions'] = mentoringProgramReportService.get_program_suggestions(milestones)
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.download_request:
            response = PDFTemplateResponse(request=request,
                                           template=self.template_name,
                                           filename="mentoring_report.pdf",
                                           context=self.get_context_data(),
                                           show_content_in_browser=False)
        return response

    def dispatch(self, request, *args, **kwargs):
        self.download_request = get_url_last_section(request.path) == get_url_last_section(reverse_lazy('surveys:download_program_report', kwargs=kwargs))
        if self.download_request:
            self.template_name = "surveys/mentoring_program_report_pdf.html"
        else:
            self.template_name = "surveys/mentoring_program_report.html"
        return super().dispatch(request, *args, **kwargs)


@method_decorator(user_has_supervisor_rights, name='dispatch')
class DashboardView(TemplateView):
    template_name = "surveys/dashboard.html"
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filter'] = DashboardFilter(self.request.GET.get('view_as', None),
                                            self.user_profile,
                                            self.request.GET,
                                            queryset=mentoringProgramService.get_mentoring_programs_from_process('Generic Mentoring Process'))
        context['charts'] = self.get_chart_info(context['filter'].qs)
        context['logged_user_profile'] = normalize_user_info(self.user_profile)
        return context

    def get_chart_info(self, qs):
        start_date = self.request.GET.get('start_date', None)
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        end_date = self.request.GET.get('end_date', None)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        performance_ordering = self.request.GET.get('performance_ordering', None)
        avg_performance_ordering = self.request.GET.get('avg_performance_ordering', None)

        data = dashboardService.get_dashboard_data(qs, start_date, end_date, performance_ordering, avg_performance_ordering)
        return data

    def dispatch(self, request, *args, **kwargs):
        self.user_profile = userProfileServices.get_user_profile_by_user_id(request.user.id)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(user_has_supervisor_rights, name='dispatch')
class DBExport(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content=dbExportService.DBExport(DashboardFilter(request.GET.get('view_as', None),
                                                                                 request.user.userprofile,
                                                                                 request.GET,
                                                                                 queryset=mentoringProgramService.get_mentoring_programs()).qs).export(),
                                content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Database Export.xlsx"'
        return response


@method_decorator(user_has_supervisor_rights, name='dispatch')
@method_decorator(request_is_ajax, name="dispatch")
class DashboardSliceTV(TemplateView):
    template_name = "surveys/dashboard_snippets/dashboard_slice_data.html"
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filter'] = DashboardSliceFilter(self.request.GET.get('view_as', None),
                                                 self.user_profile,
                                                 self.request.GET,
                                                 queryset=mentoringProgramService.get_mentoring_programs_from_process('Generic Mentoring Process'))
        category = self.request.GET.get('category')
        if not category:
            context['programs'] = []
        elif category == 'evaluation':
            context['programs'], context['applied_filters'] = dashboardSliceService.get_evaluation_filtered_programs(context['filter'].qs,
                                                                                                                     self.request.GET.get('target'),
                                                                                                                     self.request.GET.get('a_template'),
                                                                                                                     self.request.GET.get('q_nr'))
        elif category == 'monitoring':
            context['programs'], context['applied_filters'] = dashboardSliceService.get_monitoring_filtered_programs(context['filter'].qs,
                                                                                                                     self.request.GET.get('target'),
                                                                                                                     self.request.GET.get('a_template'),
                                                                                                                     self.request.GET.get('q_nr'))
        elif category == 'survey_status':
            context['programs'], context['applied_filters'] = dashboardSliceService.get_survey_status_filtered_programs(context['filter'].qs,
                                                                                                                        self.request.GET.get('status'),
                                                                                                                        self.request.GET.get('target'))
        elif category == 'program_status':
            context['programs'], context['applied_filters'] = dashboardSliceService.get_program_status_filtered_programs(context['filter'].qs,
                                                                                                                         self.request.GET.get('status'))
        elif category == 'program_start_date':
            context['programs'], context['applied_filters'] = dashboardSliceService.get_program_start_date_filtered_programs(context['filter'].qs,
                                                                                                                             self.request.GET.get('status'))
        elif category == 'mentor_statistics':
            context['programs'], context['applied_filters'] = dashboardSliceService.get_mentor_statistics_filtered_programs(context['filter'].qs,
                                                                                                                            self.request.GET.get('status'),
                                                                                                                            self.request.GET.get('target'))
        start_date = self.request.GET.get('start_date', '-')
        end_date = self.request.GET.get('end_date', '-')
        context['start_date_filter'] = start_date if start_date != '' else '-'
        context['end_date_filter'] = end_date if end_date != '' else '-'
        context['view_as'] = self.request.GET.get('view_as')
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user_profile = userProfileServices.get_user_profile_by_user_id(request.user.id)
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({'html_form': render_to_string(self.template_name, context, request=self.request)})


@user_has_supervisor_rights
def get_user_suggestions(request):
    if request.method == "GET":
        search_text = request.GET.get('search_text')
        user_type = request.GET.get('user_type')
        inputs = []
        if search_text and isinstance(search_text, str):
            inputs = search_text.lower().split("_")
        if inputs:
            filters = Q()
            for string in inputs:
                filters &= Q(username__icontains=string) | Q(first_name__icontains=string) | Q(last_name__istartswith=string)

            userprofile = userProfileServices.get_user_profile_by_user_username(request.user.username)
            if userprofile.access_level != AccessLevel.HR.value:
                if user_type in ['supervisor', 'supervisor_subordinate']:
                    filters = filters & Q(userprofile__access_level__gte=AccessLevel.SUPERVISOR.value)
                    if user_type == 'supervisor_subordinate':
                        filters = filters & Q(userprofile__hierarchy_id__startswith=userprofile.hierarchy_id + "-")

            return JsonResponse([f'{user.first_name} {user.last_name} ({user.username})' for user in userServices.get_n_users(filters, AUTOCOMPLETE_DROPDOWN_LINES)],
                                safe=False)
        return JsonResponse([], safe=False)
