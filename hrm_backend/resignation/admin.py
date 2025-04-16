from django.contrib import admin
from .models import Resignation

class ResignationAdmin(admin.ModelAdmin):
    list_display = ('resignation_id', 'employee_id', 'submission_date', 'approval_status', 'clearance_status', 'created_at', 'updated_at')
    search_fields = ('resignation_id', 'employee_id', 'approval_status')
    list_filter = ('approval_status', 'clearance_status')
    ordering = ('-created_at',)
    readonly_fields = ('resignation_id', 'submission_date', 'created_at', 'updated_at')

admin.site.register(Resignation, ResignationAdmin)
