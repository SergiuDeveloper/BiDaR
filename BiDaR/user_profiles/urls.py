from django.urls import path

from . import views

urlpatterns = [
    path('profile/login/', views.LogIn, name='logIn'),
    path('profile/preference_suggestions/', views.searchPreference),
    path('profile/<slug:user_id>/', views.ProfiletView, name='profile'),
]