from django.db import models
from departments.models import Department
from positions.models import Position
from employees.models import Employee
from django.utils import timezone
import uuid

class Job_Posting(models.Model):
    EMPLOYMENT_TYPES = [
        ('Regular', 'Regular'),
        ('Contractual', 'Contractual'),
        ('Seasonal', 'Seasonal'),
    ]

    FINANCE_APPROVAL_STATUSES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    POSTING_STATUSES = [
        ('Draft', 'Draft'),
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    ]

    job_id = models.CharField(max_length = 255, primary_key = True)
    dept = models.ForeignKey(Department, on_delete = models.SET_NULL, null = True, blank = True)
    position = models.ForeignKey(Position, on_delete = models.SET_NULL, null = True, blank = True)
    position_title = models.CharField(max_length = 100)
    description = models.TextField()
    requirements = models.TextField()
    employment_type = models.CharField(max_length = 20, choices = EMPLOYMENT_TYPES, default = 'Full-Time')
    base_salary = models.DecimalField(max_digits = 10, decimal_places = 2)
    daily_rate = models.DecimalField(max_digits = 10, decimal_places = 2)
    duration_days = models.PositiveSmallIntegerField(null = True, blank = True)
    finance_approval = models.ForeignKey(Employee, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'approved_postings')
    finance_approval_status = models.CharField(max_length=20, choices = FINANCE_APPROVAL_STATUSES, default = 'Pending')
    posting_status = models.CharField(max_length=20, choices = POSTING_STATUSES, default = 'Draft')
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.position_title} ({self.job_id})"

    @staticmethod
    def generate_job_id():
        unique_part = str(uuid.uuid4().hex)[:6].upper()
        return f"JOB-{timezone.now().year}-{unique_part}"

    def save(self, *args, **kwargs):
        if self.finance_approval_status == 'Approved':
            self.posting_status = 'Open'
        elif self.finance_approval_status == 'Rejected':
            self.posting_status = 'Closed'
        elif self.finance_approval_status == 'Pending':
            self.posting_status = 'Draft'

        super(Job_Posting, self).save(*args, **kwargs)
        
    class Meta:
        db_table = 'job_posting'  # Explicitly tell Django to use this table name
        managed = False  # Since the table already exists in your database
