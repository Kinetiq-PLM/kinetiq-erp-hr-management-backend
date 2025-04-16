from django.db import models
from job_posting.models import Job_Posting
from django.utils import timezone
from rest_framework import serializers
import uuid

APPLICATION_STATUS_CHOICES = [
    ('Applied', 'Applied'),
    ('Reviewed', 'Reviewed'),
    ('Interviewed', 'Interviewed'),
    ('Offered', 'Offered'),
    ('Hired', 'Hired'),
    ('Rejected', 'Rejected'),
]

class Candidate(models.Model):
    candidate_id = models.CharField(primary_key = True, max_length = 255)
    job = models.ForeignKey(Job_Posting, on_delete = models.CASCADE, related_name = 'candidates')
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 100, unique = True)
    phone = models.CharField(max_length = 20)
    resume_path = models.TextField()
    application_status = models.CharField(max_length = 50, choices=APPLICATION_STATUS_CHOICES, default = 'Applied')
    documents = models.JSONField(default = dict, blank = True)
    interview_details = models.JSONField(default  =dict, blank = True)
    offer_details = models.JSONField(default = dict, blank = True)
    contract_details = models.JSONField(default = dict, blank = True)
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.candidate_id}"

    @staticmethod
    def generate_candidate_id():
        return f"HR-CAND-{uuid.uuid4().hex[:6]}"
    
    class Meta:
        db_table = 'candidates'
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"