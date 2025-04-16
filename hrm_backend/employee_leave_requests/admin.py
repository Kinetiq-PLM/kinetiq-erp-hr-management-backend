from django.contrib import admin
from django import forms
from .models import Employee_Leave_Request
from employees.models import Employee
from department_superiors.models import Department_Superior

@admin.register(Employee_Leave_Request)
class Employee_Leave_RequestAdmin(admin.ModelAdmin):
    list_display = (
        'leave_id',
        'get_employee_id',
        'get_employee_name',
        'get_dept_id',
        'get_dept_name',
        'get_immediate_superior_id',
        'get_immediate_superior_name',
        'get_management_approval_id',
        'get_management_approval_name',
        'leave_type',
        'start_date',
        'end_date',
        'total_days',
        'status',
        'is_paid',
        'created_at',
        'updated_at',
    )
    list_filter = ("leave_type", "status", "is_paid")
    search_fields = ("employee_name", "leave_type", "status")
    readonly_fields = ("created_at", "updated_at")

    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = "Employee ID"

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    get_employee_name.short_description = 'Employee Name'

    def get_dept_id(self, obj):
        return obj.employee.dept.dept_id if obj.employee and obj.employee.dept else None


    def get_dept_name(self, obj):
            try:
                return obj.employee.dept.dept_name
            except AttributeError:
                return None
    get_dept_name.short_description = "Department Name"

    def get_immediate_superior_id(self, obj):
        if obj.employee and obj.employee.dept and obj.employee.position:
            try:
                superior = Department_Superior.objects.get(
                    dept=obj.employee.dept,
                    position=obj.employee.position,
                    is_archived = False
                )
                return superior.dept_superior_id
            except Department_Superior.DoesNotExist:
                return "N/A"
        return "N/A"
    get_immediate_superior_id.short_description = "Immediate Superior ID"

    def get_immediate_superior_name(self, obj):
        if obj.immediate_superior_id:
            try:
                superior = Employee.objects.get(employee_id = obj.immediate_superior_id)
                return f"{superior.first_name} {superior.last_name}"
            except Employee.DoesNotExist:
                return "N/A"
        return "N/A"
    get_immediate_superior_name.short_description = "Immediate Superior Name"

    def get_management_approval_id(self, obj):
        return obj.management_approval.dept_superior_id if obj.management_approval else None
    get_management_approval_id.short_description = "Management Approval ID"

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if obj is None:
            form.base_fields['change_reason'].required = False
            form.base_fields['change_reason'].widget = forms.HiddenInput()
        return form

    def get_management_approval_name(self, obj):
        if obj.management_approval_id:
            try:
                management_approval = Employee.objects.get(employee_id = obj.management_approval_id)
                return f"{management_approval.first_name} {management_approval.last_name}"
            except Employee.DoesNotExist:
                return "N/A"
        return "N/A"
    get_management_approval_name.short_description = "Management Approval Name"

