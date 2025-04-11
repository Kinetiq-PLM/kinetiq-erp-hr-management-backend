from django.contrib import admin
from .models import Attendance_Tracking
from employees.models import Employee
from departments.models import Department
from departments.models import Department
from django.contrib.admin import SimpleListFilter

# filtering don't remove (all of them are the same on all submodules) 
class ActiveDepartment_Filter(SimpleListFilter):
    title = 'Department'
    parameter_name = 'dept'

    def lookups(self, request, model_admin):
        active_departments = Department.objects.filter(is_archived = False)
        return [(dept.pk, dept.dept_name) for dept in active_departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(dept__pk=self.value())
        return queryset


@admin.register(Attendance_Tracking)
class Attendance_Tracking_Admin(admin.ModelAdmin):
    list_display = (
        'attendance_id',
        'get_employee_id',
        'date',
        'get_first_name',
        'get_last_name',
        'get_dept_name',
        'time_in',
        'time_out',
        'status',
        'late_hours',
        'undertime_hours',
        'is_holiday',
        # 'work_hours', same issue, dont know gagawin dito again
        'created_at',
        'updated_at',
    )

    search_fields = ('attendance_id', 'employee__employee_id', 'status')
    list_filter = ('status', 'is_holiday', ActiveDepartment_Filter,)
    list_display_links = None

    # update: added names and dept name

    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = "Employee ID"

    def get_first_name(self, obj):
        return obj.employee.first_name
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.employee.last_name
    get_last_name.short_description = "Last Name"

    def get_dept_name(self, obj):
        dept = Department.objects.filter(dept_id=obj.employee.dept_id).first()
        return dept.dept_name if dept else "-"
    get_dept_name.short_description = "Department"
