from django.contrib import admin
from .models import EmployeeSalary

@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ("salary_id", "employee_id", "base_salary", "daily_rate", "contract_start_date", "contract_end_date", "effective_date", "created_at", "updated_at")
    search_fields = ("salary_id", "employee_id")

    class Media:
        js = ('admin/js/hide_fields.js',)
