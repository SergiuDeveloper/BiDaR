from django.urls import path

from . import views

urlpatterns = [
    path('profile/pick_user/', views.PickUserView, name='pick_user'),
    path('profile/add_user/', views.AddUserView, name='add_user'),
    path('profile/<slug:user_id>/', views.ProfiletView, name='profile'),
]