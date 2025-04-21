from django.contrib import admin
from .models import Employee_Performance
from employees.models import Employee

@admin.register(Employee_Performance)
class Employee_Performance_Admin(admin.ModelAdmin):
    list_display = (
        'performance_id',
        'get_employee_id',
        'get_employee_name',
        'get_immediate_superior_id',
        'get_immediate_superior_name',
        'rating',
        'bonus_amount',
        'bonus_payment_month',
        'review_date',
        'updated_at'
    )
    search_fields = ('performance_id', 'employee__employee_id', 'immediate_superior__employee_id')
    list_filter = ("rating", "updated_at", "review_date")

    def get_employee_id(self, obj):
        return obj.employee.employee_id if obj.employee else "N/A"
    get_employee_id.short_description = 'Employee ID'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else "N/A"
    get_employee_name.short_description = 'Employee Name'

    def get_immediate_superior_id(self, obj):
        return obj.immediate_superior.employee_id if obj.immediate_superior else "N/A"
    get_immediate_superior_id.short_description = 'Superior ID'

    def get_immediate_superior_name(self, obj):
        if obj.immediate_superior:
            return f"{obj.immediate_superior.first_name} {obj.immediate_superior.last_name}"
        return "N/A"
    get_immediate_superior_name.short_description = 'Superior Name'

    class Meta:
        model = Employee_Performance
        fields = ['employee', 'rating', 'bonus_amount', 'review_date', 'bonus_payment_month']

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['employee'].queryset = Employee.objects.filter(performance_reviews__isnull = True)
        return form
