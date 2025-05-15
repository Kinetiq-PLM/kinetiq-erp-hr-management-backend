from django.contrib import admin
from .models import Attendance_Tracking

@admin.register(Attendance_Tracking)
class Attendance_Tracking_Admin(admin.ModelAdmin):
    list_display = (
        'attendance_id',
        'get_employee_name',
        'date',
        'status',
        'time_in',
        'time_out',
        # 'work_hours',
        'late_hours',
        'undertime_hours',
        'overtime_hours',
        'is_holiday',
        'created_at',
    )
    search_fields = ('attendance_id', 'employee__employee_id', 'employee__first_name', 'employee__last_name', 'status')
    list_filter = ('status', 'is_holiday', 'date')
    ordering = ('-date',)
    
    # update: added names and dept name

    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = "Employee ID"

    def get_employee_first_name(self, obj):
        return obj.employee.first_name
    get_employee_first_name.short_description = "First Name"

    def get_employee_last_name(self, obj):
        return obj.employee.last_name
    get_employee_last_name.short_description = "Last Name"

    # def get_dept_name(self, obj):
    #     dept = Department.objects.filter(dept_id=obj.employee.dept_id).first()
    #     return dept.dept_name if dept else "-"
    # get_dept_name.short_description = "Department"
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    get_employee_name.short_description = 'Employee Name'
