from django.shortcuts import render
from markupsafe import re

# Create your views here.
def QuerieDataView(request):
    context = {"title": "Make Querries"}
    return render(request, 'querie_maker/querie_maker.html', context)
