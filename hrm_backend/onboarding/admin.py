from django.contrib import admin
from .models import Onboarding

@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    list_display = ['onboarding_id', 'candidate', 'job', 'status', 'is_archived']
    search_fields = ['onboarding_id', 'candidate__candidate_id']
    list_filter = ['status', 'is_archived']
