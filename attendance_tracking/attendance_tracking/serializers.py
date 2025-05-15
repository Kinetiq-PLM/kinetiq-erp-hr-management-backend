from rest_framework import serializers
from .models import Attendance_Tracking
from employees.models import Employee

class Attendance_Tracking_Serializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_first_name = serializers.SerializerMethodField()
    employee_last_name = serializers.SerializerMethodField()
    work_hours = serializers.SerializerMethodField()

    class Meta:
        model = Attendance_Tracking
        fields = [
            'attendance_id',
            'employee_id',
            'employee_first_name',
            'employee_last_name',
            'date',
            'time_in',
            'time_out',
            'status',
            'late_hours',
            'undertime_hours',
            'overtime_hours',
            'is_holiday',
            'holiday_type',
            'work_hours',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'employee_id': {'write_only': True}
        }

    def get_employee_first_name(self, obj):
        return obj.employee.first_name

    def get_employee_last_name(self, obj):
        return obj.employee.last_name

    def get_work_hours(self, obj):
        if obj.time_in and obj.time_out:
            duration = obj.time_out - obj.time_in
            return round(duration.total_seconds() / 3600, 2)
        return 0.0


class Attendance_Tracking_CreateSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(write_only = True)

    class Meta:
        model = Attendance_Tracking
        fields = [
            'employee_id',
            'date',
            'time_in',
            'time_out',
            'status',
            'late_hours',
            'undertime_hours',
            'overtime_hours',
            'is_holiday',
        ]

    def validate_employee_id(self, value):
        try:
            return Employee.objects.get(employee_id = value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee with this ID does not exist.")

    def create(self, validated_data):
        employee = validated_data.pop('employee_id')
        return Attendance_Tracking.objects.create(employee = employee, **validated_data)

    def update(self, instance, validated_data):
        employee = validated_data.pop('employee_id', None)
        if employee:
            instance.employee = employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance