from django.contrib import admin
from django import forms
from django.urls import path
from django.http import JsonResponse
from .models import Employee_Salary
from employees.models import Employee

class Employee_Salary_Form(forms.ModelForm):
    class Meta:
        model = Employee_Salary
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
            self.fields['daily_rate'].widget = forms.HiddenInput()
            self.fields['base_salary'].widget = forms.TextInput()
        elif emp_type in ["Seasonal", "Contractual"]:
            self.fields['base_salary'].widget = forms.HiddenInput()
            self.fields['daily_rate'].widget = forms.TextInput()

@admin.register(Employee_Salary)
class Employee_Salary_Admin(admin.ModelAdmin):
    form = Employee_Salary_Form
    list_display = (
        'salary_id',
        'get_employee_id',
        'get_employee_name',
        'base_salary',
        'daily_rate',
        'effective_date',
    )
    search_fields = ('salary_id', 'employee__employee_id', 'employee__first_name', 'employee__last_name')
    list_filter = ("effective_date", "daily_rate", "base_salary")

    def get_readonly_fields(self, request, obj=None):
        return ('employee',) if obj else ()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            salaried_employees = Employee_Salary.objects.values_list('employee_id', flat=True)
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
            employee = Employee.objects.get(employee_id=employee_id)
            return JsonResponse({'employment_type': employee.employment_type})
        except Employee.DoesNotExist:
            return JsonResponse({'employment_type': None}, status=404)

    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = 'Employee ID'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    get_employee_name.short_description = 'Employee Name'