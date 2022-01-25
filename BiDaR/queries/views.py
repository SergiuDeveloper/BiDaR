from django.shortcuts import render
from markupsafe import re

# Create your views here.
def QuerieDataView(request):
    return render(request, 'querie_maker/querie_maker.html', {})
