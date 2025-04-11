from django.contrib import admin
from .models import EmployeePerformance

@admin.register(EmployeePerformance)
class EmployeePerformanceAdmin(admin.ModelAdmin):
    list_display = (
        'performance_id', 'employee', 'immediate_superior', 'rating',
        'bonus_amount', 'review_date', 'bonus_payment_month', 'comments',
    )
    search_fields = ('performance_id', 'employee__employee_id', 'immediate_superior__employee_id')
