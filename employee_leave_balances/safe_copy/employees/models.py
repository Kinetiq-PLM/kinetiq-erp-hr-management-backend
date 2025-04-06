from django.db import models
import uuid
from datetime import date

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

    employee_id = models.CharField(max_length = 255, primary_key = True, editable = False, unique = True)
    dept_id = models.CharField(max_length = 255)
    position_id = models.CharField(max_length = 255)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    phone = models.CharField(max_length = 20)
    employment_type = models.CharField(max_length = 20, choices = EMPLOYMENT_TYPES)
    status = models.CharField(max_length = 20, choices=STATUS_CHOICES, default = 'Active')
    reports_to = models.CharField(max_length = 255, blank = True, null = True)
    is_supervisor = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    class Meta:
        db_table = 'employees'
