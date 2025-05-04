from django.contrib import admin
from .models import Overtime_Requests

@admin.register(Overtime_Requests)
class Overtime_Request_Admin(admin.ModelAdmin):
    list_display = (
        'request_id',
        'employee_id',
        'request_date',
        'overtime_hours',
        'status',
        'approved_by',
        'approval_date',
    )
    list_filter = ('status', 'request_date', 'approval_date')
    search_fields = ('request_id', 'employee_id', 'approved_by')
    ordering = ('-request_date',)
