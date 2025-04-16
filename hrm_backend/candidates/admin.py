from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        'candidate_id',
        'get_job_id',
        'get_position',
        'first_name',
        'last_name',
        'email',
        'phone',
        'application_status',
        'created_at',
    )
    list_filter = ('application_status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'candidate_id')

    def get_job_id(self, obj):
        return obj.job.job_id
    get_job_id.short_description = 'Job ID'

    def get_position(self, obj):
        return obj.job.position_title if obj.job else "-"
    get_position.short_description = 'Position'
