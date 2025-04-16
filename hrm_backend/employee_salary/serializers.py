from rest_framework import serializers
from .models import Employee_Salary
from employees.models import Employee

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
            'daily_rate',
            'effective_date',
        ]
        read_only_fields = fields

    def get_employee_id(self, obj):
        return obj.employee.employee_id

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

class Employee_Salary_CreateSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(write_only = True)

    class Meta:
        model = Employee_Salary
        fields = [
            'employee_id',
            'base_salary',
            'daily_rate',
            'effective_date',
        ]

    def validate_employee_id(self, value):
        try:
            return Employee.objects.get(employee_id = value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee with this ID does not exist.")

    def validate(self, data):
        if not data.get('base_salary') and not data.get('daily_rate'):
            raise serializers.ValidationError("Either base_salary or daily_rate must be provided.")
        return data

    def create(self, validated_data):
        employee = validated_data.pop('employee_id')
        return Employee_Salary.objects.create(employee = employee, **validated_data)

    def update(self, instance, validated_data):
        employee = validated_data.pop('employee_id', None)
        if employee:
            instance.employee = employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
