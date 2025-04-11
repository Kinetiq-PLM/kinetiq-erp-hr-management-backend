from django.db import models
from employees.models import Employee

class Workforce_Allocation(models.Model):
    allocation_id = models.CharField(primary_key = True, max_length = 255)
    request_id = models.CharField(max_length = 255, unique = True)
    requesting_dept_id = models.CharField(max_length = 255)
    required_skills = models.TextField()
    task_description = models.TextField()
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name='workforce_allocations'
    )
    current_dept_id = models.CharField(max_length = 255)
    hr_approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name='approved_allocations'
    )
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
    start_date = models.DateField(null = True, blank = True)
    end_date = models.DateField(null = True, blank = True)
    rejection_reason = models.TextField(null = True, blank = True)
    submitted_at = models.DateTimeField(null = True, blank = True)
    approved_at = models.DateTimeField(null = True, blank = True)
    is_archived = models.BooleanField(default = False)  # added archive and unarchive logic

    class Meta:
        db_table = 'workforce_allocation'
        verbose_name = "Workforce Allocation" # added para maganda tignan sa admin
        verbose_name_plural = "Workforce Allocation"

    def __str__(self):
        return f"{self.allocation_id} - {self.request_id}"
