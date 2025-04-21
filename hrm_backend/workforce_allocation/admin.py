from django.contrib import admin
from .models import Workforce_Allocation

@admin.register(Workforce_Allocation)
class Workforce_AllocationAdmin(admin.ModelAdmin):
    list_display = (
        "allocation_id",
        "request_id",
        "requesting_dept_id",
        "get_hr_approver",
        "get_employee_id",
        "get_employee_name",
        "required_skills",
        "task_description",
        "approval_status",
        "get_application_status",
        "get_submitted_at",
        "get_approved_at",
        "rejection_reason",
        "start_date",
        "end_date",
    )
    search_fields = (
        "allocation_id",
        "request_id",
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
    )

    list_filter = ("approval_status", "requesting_dept_id",)
    list_display_links = None
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id if obj.employee else "-"
    get_employee_id.short_description = "Employee ID"

    def get_hr_approver(self, obj):
        return obj.hr_approver.employee_id if obj.hr_approver else "-"
    get_hr_approver.short_description = "HR Approver"

    # added new columns

    def get_application_status(self, obj):
        return obj.status
    get_application_status.short_description = "Application Status"

    def get_submitted_at(self, obj):
        return obj.submitted_at if obj.submitted_at else "-"
    get_submitted_at.short_description = "Submitted At"

    def get_approved_at(self, obj):
        return obj.approved_at if obj.approved_at else "-"
    get_approved_at.short_description = "Approved At"

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else "-"
    get_employee_name.short_description = 'Employee Name'


