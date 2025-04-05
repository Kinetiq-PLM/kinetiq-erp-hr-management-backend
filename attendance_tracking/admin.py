from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("attendance_id", "employee_id", "time_in", "time_out", "work_hours", "status", "updated_at")
    search_fields = ("attendance_id", "employee_id", "status")
    list_filter = ("status", "updated_at")