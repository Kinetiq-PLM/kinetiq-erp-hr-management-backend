from rest_framework import serializers
from .models import WorkforceAllocation
from employees.models import Employee

class WorkforceAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkforceAllocation
        fields = "__all__"

    def validate(self, data):
        approval_status = data.get("approval_status")
        hr_approver_id = data.get("hr_approver_id")

        if approval_status == "Approved":
            if not hr_approver_id:
                raise serializers.ValidationError("HR approver is required when status is 'Approved'.")

            try:
                hr = Employee.objects.get(employee_id=hr_approver_id)
                if hr.dept_id != "D005" or hr.job_title not in ["HR Manager", "HR Officer"]:
                    raise serializers.ValidationError(
                        "HR approver must be from HR department and hold title 'HR Manager' or 'HR Officer'."
                    )
            except Employee.DoesNotExist:
                raise serializers.ValidationError("HR approver does not exist.")

        return data
