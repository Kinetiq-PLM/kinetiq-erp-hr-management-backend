from django.contrib import admin
from .models import Interview

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('interview_id', 'candidate_id', 'job_id', 'interview_date', 'status', 'rating', 'created_at', 'updated_at', 'is_archived')
    search_fields = ('interview_id', 'candidate_id', 'job_id', 'status')
    list_filter = ('status', 'is_archived')
