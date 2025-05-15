from rest_framework import serializers
from .models import Resignation

class ResignationSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return "No Employee"

    def get_employee_id(self, obj):
        if obj.employee:
            return obj.employee.employee_id
        return None

    class Meta:
        model = Resignation
        fields = [
            'resignation_id',
            'employee_id',
            'employee_name',
            'submission_date',
            'notice_period_days',
            'clearance_status',
            'reason',
            'documents',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['resignation_id', 'created_at', 'updated_at']

class ResignationCreateSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(write_only=True)

    class Meta:
        model = Resignation
        fields = [
            'employee_id',
            'employee_name',
            'reason',
            'documents',
            'submission_date',
            'clearance_status',
        ]

class ResignationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = [
            'clearance_status',
            'reason',
        ]
