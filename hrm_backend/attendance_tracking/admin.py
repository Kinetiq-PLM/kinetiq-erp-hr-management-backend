from django.contrib import admin
from .models import Attendance_Tracking
from employees.models import Employee
from departments.models import Department
from django.contrib.admin import SimpleListFilter

@admin.register(Attendance_Tracking)
class Attendance_Tracking_Admin(admin.ModelAdmin):
    list_display = (
        'attendance_id',
        'get_employee_id',
        'get_employee_name',
        'date',
        # 'get_dept_name',
        'time_in',
        'time_out',
        'status',
        'late_hours',
        'undertime_hours',
        'is_holiday',
        'work_hours',
        'created_at',
    )

    search_fields = ('attendance_id', 'employee__employee_id', 'status')
    list_filter = ('status', 'is_holiday',)

    # update: added names and dept name

    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = "Employee ID"

    # def get_dept_name(self, obj):
    #     dept = Department.objects.filter(dept_id=obj.employee.dept_id).first()
    #     return dept.dept_name if dept else "-"
    # get_dept_name.short_description = "Department"
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    get_employee_name.short_description = 'Employee Name'
