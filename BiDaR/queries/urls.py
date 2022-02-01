from django.urls import path

from . import views

urlpatterns = [
    path('querie_data/', views.QuerieDataView, name='querie_data'),
]