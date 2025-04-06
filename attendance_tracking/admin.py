from django.contrib import admin
from .models import Attendance
from employees.models import Employee
from departments.models import Department
from positions.models import Position
from django.utils.html import format_html


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "attendance_id",
        "employee_id",
        "get_first_name",
        "get_last_name",
        "get_dept_name",
        "time_in",
        "time_out",
        "work_hours",
        "status",
        "updated_at",
    )

    search_fields = ("attendance_id", "employee_id", "status")
    list_filter = ("status", "updated_at")

    # update: added names and dept name

    def get_first_name(self, obj):
        employee = Employee.objects.filter(employee_id=obj.employee_id).first()
        return employee.first_name if employee else "-"
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        employee = Employee.objects.filter(employee_id=obj.employee_id).first()
        return employee.last_name if employee else "-"
    get_last_name.short_description = "Last Name"

    def get_dept_name(self, obj):
        employee = Employee.objects.filter(employee_id=obj.employee_id).first()
        if employee:
            dept = Department.objects.filter(dept_id=employee.dept_id).first()
            return dept.dept_name if dept else "-"
        return "-"
    get_dept_name.short_description = "Department"