from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id', 'first_name', 'last_name', 'dept_id', 'position_id',
        'employment_type', 'status', 'is_supervisor', 'created_at', 'updated_at'
    )
    list_filter = ('employment_type', 'status', 'is_supervisor')
    search_fields = ('first_name', 'last_name', 'employee_id', 'phone')
    readonly_fields = ('employee_id', 'created_at', 'updated_at')
