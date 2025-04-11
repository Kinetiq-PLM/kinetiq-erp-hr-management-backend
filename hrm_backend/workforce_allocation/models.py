from django.db import models
from employees.models import Employee


class WorkforceAllocation(models.Model):
    allocation_id = models.CharField(primary_key=True, max_length=255)
    request_id = models.CharField(max_length=255, unique=True)
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workforce_allocations'
    )

    requesting_dept_id = models.CharField(max_length=255)
    current_dept_id = models.CharField(max_length=255)

    required_skills = models.TextField()
    task_description = models.TextField()

    hr_approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_allocations'
    )

    rejection_reason = models.TextField(null=True, blank=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workforce_allocation'

    def __str__(self):
        return f"{self.allocation_id} - {self.request_id}"
