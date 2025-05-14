from .models import Interview
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
import uuid

class Interview_Serializer(serializers.ModelSerializer):
    candidate_id = serializers.CharField(source='candidate.candidate_id', read_only=True)
    candidate_name = serializers.SerializerMethodField(read_only=True)
    job_id = serializers.CharField(source='job.job_id', read_only=True)
    job_title = serializers.SerializerMethodField(read_only=True)
    interviewer_id = serializers.CharField(source='interviewer.employee_id', read_only=True)
    interviewer_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Interview
        fields = [
            'interview_id', 
            'candidate', 
            'candidate_id', 
            'candidate_name',
            'job', 
            'job_id', 
            'job_title',
            'interview_date', 
            'interviewer', 
            'interviewer_id',
            'interviewer_name',
            'status', 
            'feedback', 
            'rating', 
            'created_at', 
            'updated_at', 
            'is_archived'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'candidate': {'write_only': True},
            'job': {'write_only': True},
            'interviewer': {'write_only': True},
        }

    def get_candidate_name(self, obj):
        if obj.candidate:
            return f"{obj.candidate.first_name} {obj.candidate.last_name}"
        return None
    
    def get_job_title(self, obj):
        if obj.job:
            return obj.job.position_title
        return None
    
    def get_interviewer_name(self, obj):
        if obj.interviewer:
            return f"{obj.interviewer.first_name} {obj.interviewer.last_name}"
        return None

    # Validations
    def validate_interview_date(self, value):
        if value < timezone.now():
            raise ValidationError("Interview date cannot be in the past.")
        return value

    def create(self, validated_data):
        # Generate unique ID if not provided
        if not validated_data.get('interview_id'):
            validated_data['interview_id'] = f"INTV-{uuid.uuid4().hex[:8].upper()}"
        
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_at'] = timezone.now()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {
            'interview_id': rep.get('interview_id'),
            'candidate': rep.get('candidate'),
            'job': rep.get('job'),
            'interview_date': rep.get('interview_date'),
            'interviewer': rep.get('interviewer'),
            'status': rep.get('status'),
            'feedback': rep.get('feedback'),
            'rating': rep.get('rating'),
            'created_at': rep.get('created_at'),
            'updated_at': rep.get('updated_at'),
            'is_archived': rep.get('is_archived')
        }
