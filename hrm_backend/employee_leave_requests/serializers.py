from rest_framework import serializers
from .models import Employee_Leave_Request
from employees.models import Employee

class Employee_Leave_Request_Serializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source = 'employee.employee_id')
    employee_name = serializers.SerializerMethodField()
    immediate_superior_name = serializers.SerializerMethodField()
    management_approval_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee_Leave_Request
        fields = [
            'leave_id',
            'employee_id',
            'employee_name',
            'immediate_superior_id',
            'immediate_superior_name',
            'management_approval_id',
            'management_approval_name', # will be dropped soon? 
            'leave_type',
            'start_date',
            'end_date',
            'total_days',
            'is_paid',
            'status',
            'created_at',
            'updated_at',
           
        ]
        read_only_fields = ['status']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_immediate_superior_name(self, obj):
        if obj.immediate_superior_id:
            try:
                superior = Employee.objects.get(employee_id = obj.immediate_superior_id)
                return f"{superior.first_name} {superior.last_name}"
            except Employee.DoesNotExist:
                return "N/A"
        return "N/A"

    def get_management_approval_name(self, obj):
        if obj.management_approval_id:
            try:
                management_approval = Employee.objects.get(employee_id = obj.management_approval_id)
                return f"{management_approval.first_name} {management_approval.last_name}"
            except Employee.DoesNotExist:
                return "N/A"
        return "N/A"

class Employee_Leave_Request_CreateSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(write_only = True)

    class Meta:
        model = Employee_Leave_Request
        fields = [
            'employee_id',
            'immediate_superior_id',
            'management_approval_id',
            'leave_type',
            'start_date',
            'end_date',
            'is_paid',
        ]

    def validate_employee_id(self, value):
        try:
            return Employee.objects.get(employee_id = value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee with this ID does not exist.")

    def create(self, validated_data):
        employee = validated_data.pop('employee_id')
        return Employee_Leave_Request.objects.create(employee = employee, **validated_data)

    def update(self, instance, validated_data):
        employee = validated_data.pop('employee_id', None)
        if employee:
            instance.employee = employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
