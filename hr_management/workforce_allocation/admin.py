from django.contrib import admin
from .models import WorkforceAllocation

@admin.register(WorkforceAllocation)
class WorkforceAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "allocation_id", "request_id", "employee_id",
        "requesting_dept_id", "approval_status", "status",
        "start_date", "end_date", "created_at", "updated_at"
    )
    search_fields = ("allocation_id", "request_id", "employee_id")
