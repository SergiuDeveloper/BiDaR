from django.urls import path

from . import views

urlpatterns = [
    path('profile/login/', views.LogIn, name='logIn'),
    path('profile/preference_suggestions/', views.searchPreference),
    path('profile/register_user/', views.RegisterUserView, name='register_user'),
    path('profile/<slug:user_id>/', views.ProfiletView, name='profile'),
]