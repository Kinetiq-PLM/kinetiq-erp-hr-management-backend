from django.contrib import admin
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("leave_id", "employee", "leave_type", "start_date", "end_date", "status", "is_paid")
    list_filter = ("leave_type", "status", "is_paid")
    search_fields = ("employee__name", "leave_type", "status")
    readonly_fields = ("created_at", "updated_at")
