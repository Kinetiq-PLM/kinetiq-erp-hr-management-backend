from django.contrib import admin
from .models import Job_Posting

@admin.register(Job_Posting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        'job_id',
        'position_title',
        'get_dept_name',
        'get_position_name',
        'employment_type',
        'base_salary',
        'daily_rate',
        'duration_days',
        'finance_approval_status',
        'posting_status',
        'created_at',
        'updated_at'
    )
    search_fields = ('job_id', 'position_title', 'dept__dept_name', 'position__position_title')
    list_filter = ('employment_type', 'finance_approval_status', 'posting_status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    def get_dept_name(self, obj):
        return obj.dept.dept_name if obj.dept else None
    get_dept_name.short_description = 'Department'

    def get_position_name(self, obj):
        return obj.position.position_title if obj.position else None
    get_position_name.short_description = 'Position'
