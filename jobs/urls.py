from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('post/', views.post_job, name='post_job'),
    path('<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('my-jobs/', views.recruiter_jobs, name='recruiter_jobs'),
    path('<int:pk>/applications/', views.job_applications, name='job_applications'),
    path('application/<int:pk>/status/', views.update_application_status, name='update_application_status'),
    path('application/<int:pk>/view/', views.view_applicant, name='view_applicant'),
]
