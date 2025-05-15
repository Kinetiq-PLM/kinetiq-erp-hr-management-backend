from django.contrib import admin
from .models import Employee
from department_superiors.models import Department_Superior
from django import forms
from datetime import date
import uuid
from django.urls import reverse

@admin.register(Employee)
class Employee_Admin(admin.ModelAdmin):
    list_display = (
        'employee_id',
        'dept_id',
        'dept_name',
        'dept_superior_name',
        'position_id',
        'position_title',
        'first_name',
        'last_name',
        'phone',
        'employment_type',
        'status',
        'is_supervisor',
        'salary_grade',
        'reports_to',
        'created_at',
        'updated_at',
        'is_archived',
    )

    list_filter = ('employee_id',   'employment_type', 'status', 'is_supervisor')
    search_fields = ('first_name', 'last_name', 'employee_id', 'phone')
    readonly_fields = ('employee_id', 'created_at', 'updated_at', 'id_card_photo')

    def department(self, obj):
        return obj.dept.dept_name if obj.dept else 'N/A'
    
    def dept_name(self, obj):
        return obj.dept.dept_name if obj.dept else 'N/A'
    
    def dept_superior_name(self, obj):
        dept_superior = Department_Superior.objects.filter(dept=obj.dept, is_archived=False).first()
        if dept_superior:
            emp = dept_superior.get_employee()
            if emp:
                return f"{emp.first_name} {emp.last_name}"
        return 'N/A'
    dept_superior_name.short_description = 'Dept. Superior'

    def position(self, obj):
        return obj.position.position_title if obj.position else 'N/A'
    
    def position_title(self, obj):
        return obj.position.position_title if obj.position else 'N/A'
    position_title.short_description = 'Position Title'

    def salary_grade(self, obj):
        return obj.position.salary_grade if obj.position else 'N/A'
    salary_grade.short_description = 'Salary Grade'

    def save_model(self, request, obj, form, change):
            if not obj.employee_id:
                obj.employee_id = f"HR-EMP-{date.today().year}-{uuid.uuid4().hex[:6]}".upper()
            obj.save()

    def get_change_url(self, obj):
        if obj and obj.employee_id:
            return reverse('admin:employees_employee_change', args=[obj.employee_id])
        return None
