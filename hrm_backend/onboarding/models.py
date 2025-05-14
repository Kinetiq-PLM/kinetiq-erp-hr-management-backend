from django.db import models
from candidates.models import Candidate
from job_posting.models import Job_Posting

class Onboarding(models.Model):
    onboarding_id = models.CharField(primary_key = True, max_length = 255)
    candidate = models.ForeignKey(Candidate, on_delete = models.CASCADE, blank=True, null=True)
    job = models.ForeignKey(Job_Posting, on_delete = models.CASCADE, blank=True, null=True)
    offer_details = models.JSONField(default = dict, blank=True, null=True)
    contract_details = models.JSONField(default = dict, blank=True, null=True)
    status = models.CharField(max_length = 50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now = True, blank=True, null=True)
    is_archived = models.BooleanField(default = False, blank=True, null=True)

    def __str__(self):
        return f"Onboarding {self.onboarding_id} - Candidate {self.candidate_id if self.candidate_id else 'None'}"

    class Meta:
        db_table = 'onboarding'
        managed = False
