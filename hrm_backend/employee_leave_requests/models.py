from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import random
import string

class Employee_Leave_Request(models.Model):
    leave_id = models.CharField(max_length=255, primary_key=True, editable=False)
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    dept = models.ForeignKey('departments.Department', db_column='dept_id', on_delete=models.CASCADE)
    immediate_superior = models.ForeignKey("department_superiors.Department_Superior", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_leaves")
    management_approval = models.ForeignKey("department_superiors.Department_Superior", on_delete=models.SET_NULL, null=True, blank=True, related_name="management_approved_leaves")
    leave_type = models.CharField(max_length=20, choices=[
        ('Sick', 'Sick'), 
        ('Vacation', 'Vacation'), 
        ('Emergency', 'Emergency'),
        ('Maternity', 'Maternity'),
        ('Paternity', 'Paternity'),
        ('Solo Parent', 'Solo Parent'),
        ('Unpaid', 'Unpaid')
    ])
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField(null=True, blank=True)  # Make this nullable
    is_paid = models.BooleanField(default=True)
    status = models.CharField(max_length=50, default="Pending", choices=[
        ("Pending", "Pending"), 
        ("Approved by Superior", "Approved by Superior"),
        ("Rejected by Superior", "Rejected by Superior"),
        ("Approved by Management", "Approved by Management"),
        ("Rejected by Management", "Rejected by Management"),
        ("Recorded in HRIS", "Recorded in HRIS"),
        ("Approved", "Approved"), 
        ("Rejected", "Rejected"),
        ("Archived", "Archived")
    ])
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    # This method should be called during save to handle validation without raising exceptions
    def validate_leave_request(self):
        """
        Validates the leave request and returns a tuple (is_valid, error_message)
        """
        # Check for overlapping leave requests
        if Employee_Leave_Request.objects.exclude(leave_id=self.leave_id).filter(
            employee=self.employee,
            status="Pending",
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exists():
            return False, "An active leave request already exists for these dates."

        # Check for past start dates - we'll skip this check for now to allow backdated entries
        # But keep the code commented for reference
        # if self.start_date < timezone.now().date():
        #     return False, "Leave request start date cannot be in the past."

        if not self.leave_type:
            return False, "Leave type is required."
            
        # Check if end date is after start date
        if self.end_date < self.start_date:
            return False, "End date must be after start date."
            
        return True, ""

    def clean(self):
        """
        Override clean method for model validation
        This will be called by Django forms and admin, but not directly by the REST API
        """
        is_valid, error_message = self.validate_leave_request()
        if not is_valid:
            raise ValidationError(error_message)

    def generate_leave_id(self):
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        current_month = timezone.now().strftime("%m")
        current_year = timezone.now().strftime("%Y")
        return f"LV-{current_year}{current_month}-{random_part}"

    def save(self, *args, **kwargs):
        if not self.leave_id:
            self.leave_id = self.generate_leave_id()
            
        # Calculate total_days if not provided
        if self.start_date and self.end_date and self.total_days is None:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} Leave ({self.leave_type}) from {self.start_date} to {self.end_date}"

    class Meta:
            db_table = "leave_requests"
            verbose_name = "Employee Leave Request"
            verbose_name_plural = "Employee Leave Requests"