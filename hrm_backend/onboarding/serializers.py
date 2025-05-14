from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Onboarding
from candidates.models import Candidate
from job_posting.models import Job_Posting
from candidates.serializers import Candidate_Serializer
from job_posting.serializers import Job_Posting_Serializer

class Onboarding_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Onboarding
        fields = [
            'onboarding_id',
            'candidate',
            'job',
            'offer_details',
            'contract_details',
            'status',
            'created_at',
            'updated_at',
            'is_archived'
        ]

    def validate_onboarding_id(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.onboarding_id == value:
            return value
        if Onboarding.objects.filter(onboarding_id=value).exists():
            raise ValidationError(f"Onboarding ID '{value}' already exists.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        
        # Retrieve candidate details for display
        candidate_id = rep.get('candidate')
        candidate_name = "Unknown"
        try:
            if candidate_id:
                candidate = Candidate.objects.filter(candidate_id=candidate_id).first()
                if candidate:
                    candidate_name = f"{candidate.first_name} {candidate.last_name}"
        except Exception as e:
            print(f"Error fetching candidate details: {str(e)}")
        
        # Retrieve job details for display
        job_id = rep.get('job')
        job_title = "Unknown Position"
        try:
            if job_id:
                job = Job_Posting.objects.filter(job_id=job_id).first()
                if job:
                    job_title = job.position_title
        except Exception as e:
            print(f"Error fetching job details: {str(e)}")
        
        return {
            'onboarding_id': rep.get('onboarding_id'),
            'candidate_id': candidate_id,  # Keep the ID for reference
            'candidate': candidate_name,   # Add the full name
            'job_id': job_id,              # Keep the job ID for reference
            'job': job_title,              # Add the job title
            'offer_details': rep.get('offer_details') or {},
            'contract_details': rep.get('contract_details') or {},
            'status': rep.get('status'),
            'created_at': rep.get('created_at'),
            'updated_at': rep.get('updated_at'),
            'is_archived': rep.get('is_archived', False),
        }
