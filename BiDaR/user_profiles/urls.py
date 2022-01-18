from django.urls import path

from . import views

urlpatterns = [
    path('profile/<int:user_id>/', views.ProfiletView, name='profile'),
    path('profile/preference_suggestions/', views.searchPreference, name='profile'),
]