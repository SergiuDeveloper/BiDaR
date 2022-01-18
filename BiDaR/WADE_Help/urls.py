from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'surveys'

handler404 = 'handlers.http_response_status_code.handler404'

urlpatterns = [

    # MENTORING PROGRAM
    path('mentoring_programs/', views.MentoringProgramLV.as_view(), name='mentoring_programs'),  # see all mentoring programs created by a specific user
    path('mentoring_programs/<int:mentoring_program_id>/', views.MentoringProgramDV.as_view(), name='program_view'),  # see a specific mentoring program
    path('mentoring_programs/<int:mentoring_program_id>/delete', views.MentoringProgramSimpleDelV.as_view(), name='delete_mentoring_program'),  # delete a specific mentoring program
    path('mentoring_programs/<int:mentoring_program_id>/interrupt', views.MentoringProgramInterruptUV.as_view(), name='interrupt_mentoring_program'),  # interrupt a specific mentoring program
    path('mentoring_programs/<int:mentoring_program_id>/edit', views.MentoringProgramEditTV.as_view(), name='edit_mentoring_program'),  # edit a specific mentoring program
    path('mentoring_programs/<int:mentoring_program_id>/report/', views.MentoringProgramReportDV.as_view(), name='program_report'),
    path('mentoring_programs/<int:mentoring_program_id>/report/download/', views.MentoringProgramReportDV.as_view(), name='download_program_report'),
    path('add_mentoring_program/', views.MentoringProgramFV.as_view(), name='add_mentoring_program'),  # create a mentoring program

    # DASHBOARD
    path('mentoring_programs/dashboard/', views.DashboardView.as_view(), name="dashboard"),
    path('mentoring_programs/dashboard/slice/', views.DashboardSliceTV.as_view(), name='dashboard_slice'),
    path('mentoring_programs/db_export/', views.DBExport.as_view(), name="db_export"),


    # PROCESSES
    path('processes/', views.MentoringProcessesLV.as_view(), name='processes'),  # see all processes created by a specific user
    path('processes/<int:process_id>/', views.MentoringProcessDV.as_view(), name='process'),  # see the information of a specific process

    # SURVEYS
    path('surveys/', views.SurveyListLV.as_view(), name='survey_list'),  # see all surveys created by a specific user
    path('surveys/<int:survey_id>/', views.ConfigSurveyDV.as_view(), name='survey_view'),  # see all questions of a specific survey template

    # ANSWERS
    path('answer_survey/<int:survey_progress_id>/', views.AnswerSurvey.as_view(), name='answer_survey'),  # answer a specific survey progress
    path('view_answers/<int:survey_progress_id>/', views.ViewAnswersDV.as_view(), name='view_answers'),  # see the answers of a submitted survey

    # EXTRA API
    path('milestones/', views.MilestoneForAProcess.as_view(), name='get_milestones_for_a_process'),  # get all milestones for a specific process
    path('users/suggestions/', views.get_user_suggestions, name='get_user_suggestions'),  # get user suggestions for the given input
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
