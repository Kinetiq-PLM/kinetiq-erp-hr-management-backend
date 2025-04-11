from django.db import models
from django.utils import timezone
import uuid
from departments.models import Department
from positions.models import Position


class Employee(models.Model):
    EMPLOYMENT_TYPES = [
        ('Regular', 'Regular'),
        ('Contractual', 'Contractual'),
        ('Seasonal', 'Seasonal'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    employee_id = models.CharField(
        max_length = 255,
        primary_key = True,
        editable = False,
        unique = True,
    )
    user_id = models.CharField(max_length = 255, blank = True, null = True)
    dept = models.ForeignKey(Department, on_delete = models.CASCADE, null = True, blank = True)
    position = models.ForeignKey(Position, on_delete = models.CASCADE, null = True, blank = True)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    phone = models.CharField(max_length = 20)
    employment_type = models.CharField(max_length = 20, choices = EMPLOYMENT_TYPES)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'Active')
    reports_to = models.CharField(max_length = 255, blank = True, null = True)
    is_supervisor = models.BooleanField(default = False)
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False) 


    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    class Meta:
        db_table = 'employees'
