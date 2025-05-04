from django.db import models
from candidates.models import Candidate
from job_posting.models import Job_Posting

class Onboarding(models.Model):
    onboarding_id = models.CharField(primary_key = True, max_length = 255)
    candidate = models.ForeignKey(Candidate, on_delete = models.CASCADE)
    job = models.ForeignKey(Job_Posting, on_delete = models.CASCADE)
    offer_details = models.JSONField(default = dict)
    contract_details = models.JSONField(default = dict)
    status = models.CharField(max_length = 50)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False)

    def __str__(self):
        return f"Onboarding {self.onboarding_id} - Candidate {self.candidate_id}"
