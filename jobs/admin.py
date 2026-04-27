from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'recruiter', 'job_type', 'location', 'is_active', 'created_at']
    list_filter = ['job_type', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'required_skills']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['seeker', 'job', 'status', 'ats_score', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['seeker__user__username', 'job__title']
