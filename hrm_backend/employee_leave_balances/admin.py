from django.contrib import admin
from .models import Employee_Leave_Balance

@admin.register(Employee_Leave_Balance)
class Employee_Leave_BalanceAdmin(admin.ModelAdmin):
    list_display = (
        'balance_id',
        'get_employee_id',
        'get_employee_name',
        'year',
        'sick_leave_remaining',
        'vacation_leave_remaining',
        'maternity_leave_remaining',
        'paternity_leave_remaining',
        'solo_parent_leave_remaining',
        'unpaid_leave_taken',
    )
    search_fields = ('employee__first_name', 'employee__last_name', 'year')
    readonly_fields = ('balance_id', 'employee', 'year')
    list_filter = ('year',)

    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = 'Employee ID'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    get_employee_name.short_description = 'Employee Name'
