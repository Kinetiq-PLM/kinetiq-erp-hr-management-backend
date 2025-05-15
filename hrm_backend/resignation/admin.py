from django.contrib import admin
from .models import Resignation

class ResignationAdmin(admin.ModelAdmin):
    list_display = ('resignation_id', 'employee_id', 'submission_date', 'clearance_status', 'created_at', 'updated_at')
    search_fields = ('resignation_id', 'employee_id')
    list_filter = ('employee_id', 'clearance_status')
    ordering = ('created_at',)
    readonly_fields = ('resignation_id', 'submission_date', 'documents', 'created_at', 'updated_at')

admin.site.register(Resignation, ResignationAdmin)
