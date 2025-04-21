from django.contrib import admin
from .models import Payroll

@admin.action(description = "Mark payroll as Finalized")
def mark_as_finalized(modeladmin, request, queryset):
    queryset.update(status='Finalized')

@admin.action(description = "Lock payroll")
def lock_payroll(modeladmin, request, queryset):
    queryset.update(status = 'Locked')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        'payroll_id',
        'employee_id',
        'pay_period_start',
        'pay_period_end',
        'employment_type',
        'base_salary',
        'overtime_hours',
        'overtime_pay',
        'holiday_pay',
        'bonus_pay',
        'thirteenth_month_pay',
        'gross_pay',
        'sss_contribution',
        'philhealth_contribution',
        'pagibig_contribution',
        'tax',
        'late_deduction',
        'absent_deduction',
        'undertime_deduction',
        'total_deductions',
        'net_pay',
        'status',
    ]
    list_filter = ['status', 'pay_period_start', 'pay_period_end']
    search_fields = ['payroll_id', 'employee_id']
    readonly_fields = ['gross_pay', 'total_deductions', 'net_pay']
    actions = [mark_as_finalized, lock_payroll]

