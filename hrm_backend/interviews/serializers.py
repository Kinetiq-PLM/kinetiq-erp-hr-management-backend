from .models import Interview
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
import uuid
from django.db import connection

class Interview_Serializer(serializers.ModelSerializer):
    # Add extra name fields for related objects
    candidate_name = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    interviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Interview
        fields = [
            'interview_id', 
            'candidate_id',
            'candidate_name',
            'job_id', 
            'job_title',
            'interview_date', 
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

    def get_direct_field_value(self, interview_id, field_name):
        """Directly get a field value from the database for an interview"""
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {field_name} FROM human_resources.interviews WHERE interview_id = %s",
                [interview_id]
            )
            result = cursor.fetchone()
            if result:
                return result[0]
        return None

    def get_candidate_id(self, obj):
        """Get the candidate_id directly from database"""
        return self.get_direct_field_value(obj.interview_id, 'candidate_id')
        
    def get_job_id(self, obj):
        """Get the job_id directly from database"""
        return self.get_direct_field_value(obj.interview_id, 'job_id')
        
    def get_interviewer_id(self, obj):
        """Get the interviewer_id directly from database"""
        return self.get_direct_field_value(obj.interview_id, 'interviewer_id')
        
    def get_candidate_name(self, obj):
        """Get candidate name using a direct database join query"""
        candidate_id = obj.candidate_id_id if hasattr(obj, 'candidate_id_id') else self.get_candidate_id(obj)
        if not candidate_id:
            return None
            
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT first_name, last_name 
                FROM human_resources.candidates 
                WHERE candidate_id = %s
                """,
                [candidate_id]
            )
            result = cursor.fetchone()
            if result:
                return f"{result[0]} {result[1]}"
        return None
        
    def get_job_title(self, obj):
        """Get job title using a direct database join query"""
        job_id = obj.job_id_id if hasattr(obj, 'job_id_id') else self.get_job_id(obj)
        if not job_id:
            return None
            
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT position_title 
                FROM human_resources.job_posting 
                WHERE job_id = %s
                """,
                [job_id]
            )
            result = cursor.fetchone()
            if result:
                return result[0]
        return None
        
    def get_interviewer_name(self, obj):
        """Get interviewer name using a direct database join query"""
        interviewer_id = obj.interviewer_id_id if hasattr(obj, 'interviewer_id_id') else self.get_interviewer_id(obj)
        if not interviewer_id:
            return None
            
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT first_name, last_name 
                FROM human_resources.employees 
                WHERE employee_id = %s
                """,
                [interviewer_id]
            )
            result = cursor.fetchone()
            if result:
                return f"{result[0]} {result[1]}"
        return None

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
        
        # Add names as additional info
        rep['candidate_name'] = self.get_candidate_name(instance)  
        rep['job_title'] = self.get_job_title(instance)
        rep['interviewer_name'] = self.get_interviewer_name(instance)
        
        return rep
