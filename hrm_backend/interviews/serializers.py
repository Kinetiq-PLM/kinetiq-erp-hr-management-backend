from .models import Interview
from employees.models import Employee
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
import uuid
from django.db import connection

class Interview_Serializer(serializers.ModelSerializer):
    interviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            'interview_id',
            'candidate_id',
            'job_id',
            'interviewer',
            'interviewer_id',
            'interviewer_name',
            'interview_date',
            'status',
            'feedback',
            'rating',
            'created_at',
            'updated_at',
            'is_archived',
        ]

    def get_interviewer_name(self, obj):
        if obj.interviewer:
            return f"{obj.interviewer.first_name} {obj.interviewer.last_name}"
        return "No Interviewer"
    
    # Validations
    def validate_interview_date(self, value):
        if value < timezone.now():
            raise ValidationError("Interview date cannot be in the past.")
        return value

    def create(self, validated_data):
        # Generate unique ID if not provided
        if not validated_data.get('interview_id'):
            validated_data['interview_id'] = f"INT-{timezone.now().year}-{uuid.uuid4().hex[:6]}"
        
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_at'] = timezone.now()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Override to ensure we include our related data"""
        rep = super().to_representation(instance)
        rep = {
            'interview_id': rep.get('interview_id'),
            'candidate_id': rep.get('candidate_id'),
            'job_id': rep.get('job_id'),
            'interviewer_id': rep.get('interviewer_id'),
            'interviewer_name': rep.get('interviewer_name'),
            'interview_date': rep.get('interview_date'),
            'status': rep.get('status'),
            'feedback': rep.get('feedback'),
            'rating': rep.get('rating'),
            'created_at': rep.get('created_at'),
            'updated_at': rep.get('updated_at'),
            'is_archived': rep.get('is_archived')
        }
        return rep
