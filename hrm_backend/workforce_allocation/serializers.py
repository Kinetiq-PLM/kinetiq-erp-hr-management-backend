from rest_framework import serializers
from .models import Workforce_Allocation
from employees.models import Employee
import uuid

from rest_framework import serializers
class Workforce_Allocation_Serializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = Workforce_Allocation
        fields = [
            'allocation_id',
            'request_id',
            'requesting_dept_id',
            'current_dept_id',
            'hr_approver',
            'employee_id',
            'employee_name',
            'required_skills',
            'task_description',
            'approval_status',
            'status',
            'start_date',
            'end_date',
            'rejection_reason',
            'submitted_at',
            'approved_at',
        ]
        read_only_fields = [
            'allocation_id',
            'request_id',
            'approval_status',
            'submitted_at',
            'approved_at',
        ]

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

class Workforce_Allocation_CreateSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Workforce_Allocation
        fields = [
            'required_skills',
            'task_description',
            'requesting_dept_id',
            'current_dept_id',
            'hr_approver',
            'employee_name',
            'status',
            'start_date',
            'end_date',
        ]

    def validate(self, data):
        approval_status = data.get("approval_status")
        hr_approver = data.get("hr_approver")

        if approval_status == "Approved" and not hr_approver:
            raise serializers.ValidationError("HR approver is required when status is 'Approved'.")

        return data
    
    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None


class Workforce_Allocation_RequestSerializer(serializers.ModelSerializer):
    # employee = serializers.PrimaryKeyRelatedField(queryset = Employee.objects.all())
    employee_name = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = Workforce_Allocation
        fields = [
            'required_skills',
            'task_description',
            'requesting_dept_id',
            'start_date',
            'end_date',
        ]

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def create(self, validated_data):
        from uuid import uuid4
        validated_data['request_id'] = f"REQ-{uuid4()}"
        validated_data['allocation_id'] = f"ALLOC-{uuid4()}"
        return Workforce_Allocation.objects.create(**validated_data)
