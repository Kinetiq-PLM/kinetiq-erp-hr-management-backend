from rest_framework import serializers
from .models import Attendance_Tracking
from employees.models import Employee
from departments.models import Department

class Attendance_Tracking_Serializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance_Tracking
        fields = [
            'attendance_id',
            'employee',
            'first_name',
            'last_name',
            'date',
            'time_in',
            'time_out',
            'status',
            'late_hours',
            'undertime_hours',
            'is_holiday',
            # 'work_hours',
            'created_at',
            'updated_at',
            'is_archived',
        ]

    def get_first_name(self, obj):
        return obj.employee.first_name

    def get_last_name(self, obj):
        return obj.employee.last_name

    def get_dept_name(self, obj):
        dept = Department.objects.filter(dept_id = obj.employee.dept_id).first()
        return dept.dept_name if dept else None
