from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/seeker/', views.register_seeker, name='register_seeker'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/seeker/', views.seeker_profile, name='seeker_profile'),
    path('profile/recruiter/', views.recruiter_profile, name='recruiter_profile'),
]
