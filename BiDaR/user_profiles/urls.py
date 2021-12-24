from django.urls import path

from . import views

urlpatterns = [
    path('', views.ProfileEdtView.as_view(), name='profile'),
]