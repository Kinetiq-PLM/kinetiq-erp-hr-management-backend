from rest_framework import serializers
from .models import Employee_Performance

class Employee_Performance_Serializer(serializers.ModelSerializer):
    employee_id = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    immediate_superior_id = serializers.SerializerMethodField()
    immediate_superior_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee_Performance
        fields = [
            'performance_id',
            'employee_id',
            'employee_name',
            'immediate_superior_id',
            'immediate_superior_name',
            'rating',
            'bonus_amount',
            'review_date',
            'bonus_payment_month',
            'updated_at',
            'is_archived',
        ]
        read_only_fields = [
            'performance_id',
            'employee_id',
            'employee_name',
            'immediate_superior_id',
            'immediate_superior_name',
            'bonus_amount',
            'review_date',
            'updated_at',
            'is_archived',
        ]

    def get_employee_id(self, obj):
        return obj.employee.employee_id if obj.employee else None

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}".strip()
        return None

    def get_immediate_superior_id(self, obj):
        return obj.immediate_superior.employee_id if obj.immediate_superior else None

    def get_immediate_superior_name(self, obj):
        if obj.immediate_superior:
            return f"{obj.immediate_superior.first_name} {obj.immediate_superior.last_name}".strip()
        return None
