from rest_framework import serializers
from .models import Resignation

class ResignationSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Resignation
        fields = [
            'resignation_id',
            'employee_id',
            'submission_date',
            'notice_period_days',
            'hr_approver_id',
            'approval_status',
            'clearance_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['resignation_id', 'created_at', 'updated_at']

class ResignationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = [
            'employee_id',
            'submission_date',
            'hr_approver_id',
            'approval_status',
            'clearance_status',
        ]

class ResignationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = [
            'approval_status',
            'clearance_status',
        ]