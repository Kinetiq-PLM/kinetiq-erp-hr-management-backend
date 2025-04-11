from django.contrib import admin
from .models import Employee
from django import forms
from datetime import date
import uuid
from django.urls import reverse

@admin.register(Employee)
class Employee_Admin(admin.ModelAdmin):
    list_display = (
        'employee_id',
        'user_id',
        'dept_id',
        'department',
        'position_id',
        'position_title',
        'salary_grade',
        'first_name',
        'last_name',
        'phone',
        'employment_type',
        'status',
        'is_supervisor',
        'reports_to',
        'created_at',
        'updated_at',
        'is_archived',
    )

    list_filter = ('employment_type', 'status', 'is_supervisor')
    search_fields = ('first_name', 'last_name', 'employee_id', 'phone')
    readonly_fields = ('employee_id', 'created_at', 'updated_at')

    def department(self, obj):
        return obj.dept.dept_name if obj.dept else 'N/A'

    def position(self, obj):
        return obj.position.position_title if obj.position else 'N/A'
    
    def position_title(self, obj):
        return obj.position.position_title if obj.position else 'N/A'
    position_title.short_description = 'Position Title'

    def salary_grade(self, obj):
        return obj.position.salary_grade if obj.position else 'N/A'
    salary_grade.short_description = 'Salary Grade'

    # hide the fuckign chnag reason xd d ko matnggal HHAHAHA
    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if obj is None:
            form.base_fields['change_reason'].required = False
            form.base_fields['change_reason'].widget = forms.HiddenInput()
        return form


    def save_model(self, request, obj, form, change):
            if not obj.employee_id:
                obj.employee_id = f"HR-EMP-{date.today().year}-{uuid.uuid4().hex[:6]}".upper()
            obj.save()

    def get_change_url(self, obj):
        if obj and obj.employee_id:
            return reverse('admin:employees_employee_change', args=[obj.employee_id])
        return None
