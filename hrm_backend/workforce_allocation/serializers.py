from rest_framework import serializers
from .models import Workforce_Allocation
from employees.models import Employee

class Workforce_Allocation_Serializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Workforce_Allocation
        fields = [
            'allocation_id',
            'request_id',
            'requesting_dept_id',
            'current_dept_id',
            'employee_id',
            'employee_name',
            'required_skills',
            'task_description',
            'hr_approver',
            'approval_status',
            'status',
            'start_date',
            'end_date',
            'rejection_reason',
            'submitted_at',
            'approved_at',
            # 'updated_at',
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
    employee_name = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = Workforce_Allocation
        fields = [
            'required_skills',
            'task_description',
            'requesting_dept_id',
            'current_dept_id',
            'hr_approver',
            'employee',
            'employee_name',
            'status',
            'start_date',
            'end_date',
            'approval_status',
            'rejection_reason',
        ]

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def validate(self, data):
        """Validate the allocation data."""
        approval_status = data.get("approval_status")
        
        if approval_status == "Approved" and not data.get("hr_approver"):
            raise serializers.ValidationError({"hr_approver": "HR approver is required when status is 'Approved'."})
        
        if approval_status == "Rejected" and not data.get("rejection_reason"):
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is required when status is 'Rejected'."})
        
        return data

    def update_status(self, allocation):
        if allocation.approval_status == 'Approved':
            allocation.status = 'Active'
        elif allocation.approval_status == 'Rejected':
            allocation.status = 'Canceled'
        elif allocation.approval_status == 'Pending':
            allocation.status = 'Draft'
        allocation.save()

class Workforce_Allocation_RequestSerializer(serializers.ModelSerializer):
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

    def update_status(self, allocation):
        if allocation.approval_status == 'Approved':
            allocation.status = 'Active'
        elif allocation.approval_status == 'Rejected':
            allocation.status = 'Canceled'
        elif allocation.approval_status == 'Pending':
            allocation.status = 'Draft'
        allocation.save()