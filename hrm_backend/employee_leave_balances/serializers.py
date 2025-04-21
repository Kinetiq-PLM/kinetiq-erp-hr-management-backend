from rest_framework import serializers
from .models import Employee_Leave_Balance

class Employee_Leave_Balance_Serializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id', read_only = True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee_Leave_Balance
        fields = [
            'balance_id',
            'employee_id',
            'employee_name',
            'year',
            'sick_leave_remaining',
            'vacation_leave_remaining',
            'maternity_leave_remaining',
            'paternity_leave_remaining',
            'solo_parent_leave_remaining',
            'unpaid_leave_taken',
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else None

class Employee_Leave_Balance_CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee_Leave_Balance
        fields = [
            'employee',
            'year',
            'sick_leave_remaining',
            'vacation_leave_remaining',
            'maternity_leave_remaining',
            'paternity_leave_remaining',
            'solo_parent_leave_remaining',
            'unpaid_leave_taken',
        ]
