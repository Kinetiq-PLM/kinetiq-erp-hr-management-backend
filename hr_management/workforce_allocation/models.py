from django.db import models

class WorkforceAllocation(models.Model):
    allocation_id = models.CharField(primary_key=True, max_length=255)
    request_id = models.CharField(max_length=255, unique=True)
    requesting_dept_id = models.CharField(max_length=255)
    required_skills = models.TextField()
    task_description = models.TextField()
    employee_id = models.CharField(max_length=255, null=True, blank=True)
    current_dept_id = models.CharField(max_length=255)
    hr_approver_id = models.CharField(max_length=255, null=True, blank=True)
    
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
            ('Under Review', 'Under Review')
        ],
        default='Pending'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('Draft', 'Draft'),
            ('Submitted', 'Submitted'),
            ('Active', 'Active'),
            ('Completed', 'Completed'),
            ('Canceled', 'Canceled')
        ],
        default='Draft'
    )
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workforce_allocation'

    def __str__(self):
        return f"{self.allocation_id} - {self.request_id}"
