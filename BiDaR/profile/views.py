from django.views.generic import TemplateView
from django.shortcuts import render

class ProfileEdtView(TemplateView):
    template_name = "D:/Facultate/WADE/project/BiDaR/BiDaR/profile/templates/user_profile.html"

    def get_context_data(self, **kwargs):
        context = {}
        categories = [{'name': "a", "values" : [1,2,3]}, {'name': "b", "values" : [2,4,5]}, {'name': "c", "values" : [1,7,3,5]}]
        context["categories"] = categories
        context["list"] = [1,2,3,4,5]
        return context

def view2(request):
    context = {}
    categories = [{'name': "a", "values" : [1,2,3]}, {'name': "b", "values" : [2,4,5]}, {'name': "c", "values" : [1,7,3,5]}]
    context["categories"] = categories
    context["list"] = [1,2,3,4,5]
    return render(request, 'D:/Facultate/WADE/project/BiDaR/BiDaR/profile/templates/user_profile.html', context)