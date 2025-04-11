from rest_framework import serializers
from .models import Employee_Salary

class Employee_Salary_Serializer(serializers.ModelSerializer):
    employee_id = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee_Salary
        fields = [
            'salary_id',
            'employee_id',
            'employee_name',
            'base_salary',
            'daily_rate'
            'effective_date'
        ]

    def get_employee_id(self, obj):
        return obj.employee.employee_id

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def validate(self, data):
        if not data.get('base_salary') and not data.get('daily_rate'):
            raise serializers.ValidationError("Either base_salary or daily_rate must be provided.")
        return data
