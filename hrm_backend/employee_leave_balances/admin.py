from django.contrib import admin
from .models import Employee_Leave_Balance

@admin.register(Employee_Leave_Balance)
class Employee_Leave_BalanceAdmin(admin.ModelAdmin):
    list_display = (
        "balance_id",
        "employee_id",
        "year",
        "sick_leave_remaining",
        "vacation_leave_remaining",
        "maternity_leave_remaining",
        "paternity_leave_remaining",
        "solo_parent_leave_remaining",
        "unpaid_leave_taken",
    )
    search_fields = ("employee_id", "year")
    readonly_fields = ("balance_id", "employee_id", "year")
