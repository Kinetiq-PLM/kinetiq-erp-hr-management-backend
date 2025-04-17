from rest_framework import serializers
from .models import Workforce_Allocation
from employees.models import Employee
import uuid

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
            'approval_status',
            'rejection_reason',
        ]

    def validate(self, data):
        approval_status = data.get("approval_status")
        hr_approver = data.get("hr_approver")
        rejection_reason = data.get("rejection_reason")

        if approval_status == "Approved" and not hr_approver:
            raise serializers.ValidationError("HR approver is required when status is 'Approved'.")

        if approval_status == "Rejected" and not rejection_reason:
            raise serializers.ValidationError("Rejection reason is required when status is 'Rejected'.")

        return data

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def create(self, validated_data):
        from uuid import uuid4
        validated_data['request_id'] = f"REQ-{uuid4()}"
        validated_data['allocation_id'] = f"ALLOC-{uuid4()}"

        hr_approver = validated_data.get('hr_approver', None)
        approval_status = validated_data.get('approval_status', 'Pending')

        workforce_allocation = Workforce_Allocation.objects.create(**validated_data)

        self.update_status(workforce_allocation)

        return workforce_allocation

    def update_status(self, allocation):
        if allocation.approval_status == 'Approved':
            allocation.status = 'Active'
        elif allocation.approval_status == 'Rejected':
            allocation.status = 'Canceled'
        elif allocation.approval_status == 'Pending':
            allocation.status = 'Draft'
        allocation.save()

class Workforce_Allocation_RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workforce_Allocation
        fields = [
            'required_skills',
            'task_description',
            'requesting_dept_id',
            'start_date',
            'end_date',
        ]

    def create(self, validated_data):
        from uuid import uuid4

        # Forcefully remove any externally passed values (just to be safe)
        validated_data.pop('request_id', None)
        validated_data.pop('allocation_id', None)

        validated_data['request_id'] = f"REQ-{uuid4()}"
        validated_data['allocation_id'] = f"ALLOC-{uuid4()}"

        workforce_allocation = Workforce_Allocation.objects.create(**validated_data)

        self.update_status(workforce_allocation)
        return workforce_allocation

    def update_status(self, allocation):
        if allocation.approval_status == 'Approved':
            allocation.status = 'Active'
        elif allocation.approval_status == 'Rejected':
            allocation.status = 'Canceled'
        elif allocation.approval_status == 'Pending':
            allocation.status = 'Draft'
        allocation.save()