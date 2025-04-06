from django.contrib import admin
from .models import DepartmentSuperior
from employees.models import Employee
from positions.models import Position
from departments.models import Department

@admin.register(DepartmentSuperior)
class DepartmentSuperiorAdmin(admin.ModelAdmin):
    list_display = (
    'dept_id', 
    'get_dept_name',
    'get_employee_id',
    'get_first_name', 
    'get_last_name',
    'get_position_id',
    'superior_job_title', 
    'hierarchy_level', 
)
    # grayed out update for uneditable id and superior job title
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['dept_id', 'superior_job_title']
        return []

    # removed the add department superiors
    def has_add_permission(self, request):
        return False

    def get_dept_name(self, obj):
        dept = Department.objects.filter(dept_id=obj.dept_id).first()
        return dept.dept_name if dept else "-"
    get_dept_name.short_description = 'Department Name'

    def get_employee_id(self, obj):
        employee = Employee.objects.filter(dept_id=obj.dept_id, is_supervisor=True).first()
        return employee.employee_id if employee else "-"
    get_employee_id.short_description = 'Employee ID'

    def get_position_id(self, obj):
        employee = Employee.objects.filter(dept_id=obj.dept_id, is_supervisor=True).first()
        return employee.position_id if employee else "-"
    get_position_id.short_description = 'Position ID'

    def get_first_name(self, obj):
        employee = Employee.objects.filter(dept_id=obj.dept_id, is_supervisor=True).first()
        return employee.first_name if employee else "-"
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        employee = Employee.objects.filter(dept_id=obj.dept_id, is_supervisor=True).first()
        return employee.last_name if employee else "-"
    get_last_name.short_description = 'Last Name'
