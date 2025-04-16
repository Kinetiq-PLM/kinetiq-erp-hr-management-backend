from rest_framework import serializers
from .models import (
    Job_Posting,
    Department,
)
from department_superiors.models import Department_Superior
class Job_Posting_Serializer(serializers.ModelSerializer):
    dept_id = serializers.SerializerMethodField()
    position_id = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    finance_approval_id = serializers.SerializerMethodField()

    class Meta:
        model = Job_Posting
        fields = [
            'job_id',
            'dept_id',
            'position_id',
            'position_title',
            'description',
            'requirements',
            'employment_type',
            'base_salary',
            'daily_rate',
            'duration_days',
            'finance_approval_id',
            'finance_approval_status',
            'posting_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'job_id',
            'created_at',
            'updated_at',
            'finance_approval_id',
            'finance_approval_status',
            'posting_status',
        ]

    def get_dept_id(self, obj):
        return obj.dept.dept_id if obj.dept else None

    def get_position_id(self, obj):
        return obj.position.position_id if obj.position else None

    def get_position_title(self, obj):
        return obj.position.position_title if obj.position else None

    def get_finance_approval_id(self, obj):
        return obj.finance_approval.finance_approval_id if obj.finance_approval else None

class Job_Posting_CreateSerializer(serializers.ModelSerializer):

    dept_id = serializers.PrimaryKeyRelatedField(
        queryset = Department.objects.all(),
        source = 'dept'
    )
    
    class Meta:
        model = Job_Posting
        fields = [
            'dept_id',
            'position_id',
            'description',
            'requirements',
            'base_salary',
            'daily_rate',
            'posting_status',
        ]

class Job_Posting_RequestSerializer(serializers.ModelSerializer):
    # dept_id = serializers.PrimaryKeyRelatedField(
    #     queryset = Department.objects.all(),
    #     source = 'dept'
    # )
    class Meta:
        model = Job_Posting
        fields = [
            # 'dept_id',
            'position',
            'description',
            'requirements',
            'base_salary',
            'daily_rate',
            'posting_status',
        ]

    def create(self, validated_data):
        from uuid import uuid4
        request = self.context['request']
        
        try:
            dept_superior = Department_Superior.objects.get(user = request.user)
            validated_data['dept'] = dept_superior.department
        except Department_Superior.DoesNotExist:
            raise serializers.ValidationError("Requesting user is not a registered Department Superior.")

        validated_data['job_id'] = f"JOBREQ-{uuid4()}"
        validated_data['posting_status'] = 'Requested'
        return Job_Posting.objects.create(**validated_data)
