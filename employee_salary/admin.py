from django.contrib import admin
from django import forms
from django.urls import path
from django.http import JsonResponse
from .models import EmployeeSalary
from employees.models import Employee


class EmployeeSalaryForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee_id = self.data.get('employee') if self.data else None
        instance = kwargs.get('instance')

        if instance:
            emp_type = instance.employee.employment_type
        elif employee_id:
            try:
                emp_type = Employee.objects.get(pk=employee_id).employment_type
            except Employee.DoesNotExist:
                emp_type = None
        else:
            emp_type = None

        if emp_type == "Regular":
            self.fields['contract_start_date'].widget = forms.HiddenInput()
            self.fields['contract_end_date'].widget = forms.HiddenInput()
            self.fields['daily_rate'].widget = forms.HiddenInput()
        elif emp_type in ["Seasonal", "Contractual"]:
            self.fields['base_salary'].widget = forms.HiddenInput()


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    form = EmployeeSalaryForm
    list_display = (
        'salary_id', 'employee', 'base_salary', 'daily_rate',
        'contract_start_date', 'contract_end_date', 'effective_date',
        'created_at', 'updated_at'
    )
    search_fields = ('salary_id', 'employee__employee_id')
    # unclickable    
    def get_readonly_fields(self, request, obj=None):
        return ('employee',) if obj else ()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            salaried_employees = EmployeeSalary.objects.values_list('employee_id', flat=True)
            form.base_fields['employee'].queryset = Employee.objects.exclude(employee_id__in=salaried_employees)
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_employment_type/', self.admin_site.admin_view(self.get_employment_type)),
        ]
        return custom_urls + urls

    def get_employment_type(self, request):
        employee_id = request.GET.get('employee_id')
        try:
            employee = Employee.objects.get(pk=employee_id)
            return JsonResponse({'employment_type': employee.employment_type})
        except Employee.DoesNotExist:
            return JsonResponse({'employment_type': None}, status=404)

    class Media:
        js = [
            'admin/js/employee_salary-add.js',
            'admin/js/employee_salary-edit.js',
        ]
