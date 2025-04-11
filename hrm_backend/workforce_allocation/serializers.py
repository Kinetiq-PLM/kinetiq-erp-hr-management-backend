from rest_framework import serializers
from .models import Workforce_Allocation
from employees.models import Employee

class Workforce_Allocation_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Workforce_Allocation
        fields = [
            'allocation_id',
            'request_id',
            'required_skills',
            'approval_status',
            'submitted_at',
            'approved_at',
            'task_description',
            'requesting_dept_id',
            'current_dept_id',
            'hr_approver',
            'employee',
            'status',
            'start_date',
            'end_date',
            'rejection_reason',
        ]
        read_only_fields = [
            'allocation_id',
            'request_id',
            'required_skills',
            'approval_status',
            'submitted_at',
            'approved_at',
            'task_description',
            'requesting_dept_id',
            'current_dept_id',
            'hr_approver',
        ]

    def validate(self, data):
        approval_status = data.get("approval_status")
        hr_approver = data.get("hr_approver")

        if approval_status == "Approved":
            if not hr_approver:
                raise serializers.ValidationError("HR approver is required when status is 'Approved'.")

            if hr_approver.dept.dept_id != "D005" or hr_approver.position.position_title not in ["HR Manager", "HR Officer"]:
                raise serializers.ValidationError(
                    "HR approver must be from HR department and hold title 'HR Manager' or 'HR Officer'."
                )

        return data
