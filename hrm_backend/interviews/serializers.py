from .models import Interview
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError

class Interview_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['interview_id', 'candidate_id', 'job_id', 'interview_date', 'status', 'feedback', 'rating', 'created_at', 'updated_at', 'is_archived']

    # Validations
    def validate_interview_date(self, value):
        if value < timezone.now():
            raise ValidationError("Interview date cannot be in the past.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep = {
            'interview_id': rep.get('interview_id'),
            'candidate_id': rep.get('candidate_id'),
            'job_id': rep.get('job_id'),
            'interview_date': rep.get('interview_date'),
            'status': rep.get('status'),
            'feedback': rep.get('feedback'),
            'rating': rep.get('rating'),
            'created_at': rep.get('created_at'),
            'updated_at': rep.get('updated_at'),
            'is_archived': rep.get('is_archived')
        }
        return rep
