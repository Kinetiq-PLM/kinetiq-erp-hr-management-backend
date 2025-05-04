from django.db import models
from django.utils import timezone
from candidates.models import Candidate
from job_posting.models import Job_Posting

class Interview(models.Model):
    interview_id = models.CharField(max_length = 100, unique = True)
    candidate = models.ForeignKey(Candidate, on_delete = models.CASCADE)
    job = models.ForeignKey(Job_Posting, on_delete = models.CASCADE)
    interview_date = models.DateTimeField()
    status = models.CharField(max_length = 50)
    feedback = models.TextField()
    rating = models.SmallIntegerField()
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(default = timezone.now)
    is_archived = models.BooleanField(default = False)

    def __str__(self):
        return f"Interview {self.interview_id} for Candidate {self.candidate_id}"
