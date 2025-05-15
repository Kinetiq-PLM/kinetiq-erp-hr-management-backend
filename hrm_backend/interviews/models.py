from django.db import models
from django.utils import timezone
from employees.models import Employee
from candidates.models import Candidate
from job_posting.models import Job_Posting

class Interview(models.Model):
    interview_id = models.CharField(max_length = 100, primary_key = True)
    candidate = models.ForeignKey(Candidate, on_delete = models.CASCADE)
    job = models.ForeignKey(Job_Posting, on_delete = models.CASCADE)
    interviewer = models.ForeignKey(Employee, on_delete = models.SET_NULL, null = True, blank = True)
    interview_id = models.CharField(primary_key=True, max_length=255)
    candidate_id = models.ForeignKey('candidates.Candidate', models.DO_NOTHING, blank=True, null=True, db_column='candidate_id')
    job_id = models.ForeignKey('job_posting.Job_Posting', models.DO_NOTHING, blank=True, null=True, db_column='job_id')
    interview_date = models.DateTimeField()
    interviewer_id = models.ForeignKey('employees.Employee', models.DO_NOTHING, blank=True, null=True, db_column='interviewer_id')
    status = models.CharField(max_length=50, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    rating = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    is_archived = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        managed = False
        db_table = 'interviews'

    def __str__(self):
        return f"Interview {self.interview_id} for Candidate {self.candidate_id}"
    
    class Meta:
        db_table = "interviews"

        return f"Interview {self.interview_id} for Candidate {self.candidate_id.first_name if self.candidate_id else 'Unknown'}"

    def save(self, *args, **kwargs):
        if not self.updated_at:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
