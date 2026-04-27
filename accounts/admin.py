from django.contrib import admin
from .models import SeekerProfile, RecruiterProfile

@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile', 'experience_years', 'location', 'created_at']
    search_fields = ['user__username', 'user__email', 'skills']

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'mobile', 'location', 'created_at']
    search_fields = ['user__username', 'company_name']
