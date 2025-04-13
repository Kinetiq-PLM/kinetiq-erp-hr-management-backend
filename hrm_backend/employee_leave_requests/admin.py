from django.contrib import admin
from django import forms
from .models import Employee_Leave_Request
from department_superiors.models import Department_Superior

@admin.register(Employee_Leave_Request)
class Employee_Leave_RequestAdmin(admin.ModelAdmin):
    list_display = (
        "leave_id",
        "get_dept_id",
        "get_dept_name",
        "get_employee_id",
        "get_first_name",
        "get_last_name",
        "get_immediate_superior_id",
        "get_management_approval_id",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "is_paid",
    )
    list_filter = ("leave_type", "status", "is_paid")
    search_fields = ("employee__first_name", "employee__last_name", "leave_type", "status")
    readonly_fields = ("created_at", "updated_at")

    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = "Employee ID"

    def get_first_name(self, obj):
        return obj.employee.first_name
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.employee.last_name
    get_last_name.short_description = "Last Name"

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
                    is_archived=False
                )
                return superior.dept_superior_id
            except Department_Superior.DoesNotExist:
                return "N/A"
        return "N/A"
    get_immediate_superior_id.short_description = "Immediate Superior ID"

    def get_management_approval_id(self, obj):
        return obj.management_approval.dept_superior_id if obj.management_approval else None
    get_management_approval_id.short_description = "Management Approval ID"

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if obj is None:
            form.base_fields['change_reason'].required = False
            form.base_fields['change_reason'].widget = forms.HiddenInput()
        return form
