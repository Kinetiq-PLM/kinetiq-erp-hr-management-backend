from rest_framework import serializers
from datetime import date
from .models import Employee_Performance
from employees.models import Employee
import uuid

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
        ]
        read_only_fields = fields  # read-only for display

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

class Employee_Performance_CreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee_Performance
        fields = [
            'bonus_amount',
            'rating',
            'bonus_payment_month',
        ]

    def validate_employee_id(self, value):
        try:
            return Employee.objects.get(employee_id = value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee with this ID does not exist.")

    def validate_immediate_superior_id(self, value):
        try:
            return Employee.objects.get(employee_id = value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Immediate Superior with this ID does not exist.")

    def create(self, validated_data):
        employee = validated_data.pop('employee_id')
        immediate_superior = validated_data.pop('immediate_superior_id', None)
        
        performance_id = f"HR-REV-{date.today().year}-{uuid.uuid4().hex[:6]}".upper()

        return Employee_Performance.objects.create(
            performance_id = performance_id,
            employee = employee,
            immediate_superior = immediate_superior,
            **validated_data
        )

    def update(self, instance, validated_data):
        employee = validated_data.pop('employee_id', None)
        immediate_superior = validated_data.pop('immediate_superior_id', None)
        if employee:
            instance.employee = employee
        if immediate_superior:
            instance.immediate_superior = immediate_superior
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
