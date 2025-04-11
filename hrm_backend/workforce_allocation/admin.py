from django.contrib import admin
from .models import WorkforceAllocation


@admin.register(WorkforceAllocation)
class WorkforceAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "allocation_id",
        "request_id",
        "get_employee_id",
        "get_first_name",
        "get_last_name",
        "requesting_dept_id",
        "required_skills",
        "task_description",
        "get_hr_approver",
        "rejection_reason",
        "approval_status",
        "get_application_status",
        "get_submitted_at",
        "get_approved_at",
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
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id if obj.employee else "-"
    get_employee_id.short_description = "Employee ID"

    def get_first_name(self, obj):
        return obj.employee.first_name if obj.employee else "-"
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.employee.last_name if obj.employee else "-"
    get_last_name.short_description = "Last Name"

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
