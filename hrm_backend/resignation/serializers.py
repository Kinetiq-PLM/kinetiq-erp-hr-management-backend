from rest_framework import serializers
from .models import Resignation
from employees.models import Employee

class ResignationSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    
    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None
        
    class Meta:
        model = Resignation
        fields = [
            'resignation_id',
            'employee',
            'employee_name',
            'submission_date',
            'notice_period_days',
            'clearance_status',
            'created_at',
            'updated_at',
            'documents',
            'reason',
        ]
        read_only_fields = ['resignation_id', 'created_at', 'updated_at']

class ResignationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = [
            'employee',
            'submission_date',
            'notice_period_days',
            'clearance_status',
            'documents',
            'reason',
        ]

class ResignationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = [
            'clearance_status',
            'notice_period_days',
            'documents',
            'reason',
        ]