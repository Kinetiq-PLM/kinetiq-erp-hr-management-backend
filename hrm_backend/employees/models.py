from django.db import models
from django.apps import apps
from django.utils import timezone
from departments.models import Department
from department_superiors.models import Department_Superior
from positions.models import Position
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from datetime import date
import uuid
import re

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
    # email = models.EmailField(max_length = 255, blank = True, null = True) may gagawin pa rito sabi comment ko lang
    employment_type = models.CharField(max_length = 20, choices = EMPLOYMENT_TYPES)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'Active')
    reports_to = models.CharField(max_length = 255, blank = True, null = True)
    is_supervisor = models.BooleanField(default = False)
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False) 

    history = HistoricalRecords() # history
    change_reason = models.CharField(max_length=255, blank = True, null = True)

    # validation errors
    def clean(self):
        phone_regex = re.compile(r'^[\d\+\-\(\)\s]*$')
        if not phone_regex.match(self.phone):
            raise ValidationError(f"Phone number '{self.phone}' is invalid. Only numbers and valid characters are allowed.")
        
        name_regex = re.compile(r'^[A-Za-z\s\'-]+$')
        if not name_regex.match(self.first_name):
            raise ValidationError(f"First name '{self.first_name}' contains invalid characters. Only letters and basic punctuation are allowed.")
        if not name_regex.match(self.last_name):
            raise ValidationError(f"Last name '{self.last_name}' contains invalid characters. Only letters and basic punctuation are allowed.")
        
        if Employee.objects.filter(phone=self.phone, is_archived=False).exclude(pk=self.pk).exists():
            raise ValidationError(f"An active employee with the phone number '{self.phone}' already exists.")
        
        if Employee.objects.filter(first_name=self.first_name, last_name=self.last_name, is_archived=False).exclude(pk=self.pk).exists():
            raise ValidationError(f"An active employee with the name '{self.first_name} {self.last_name}' already exists.")
        
        if self.status == 'Inactive' and self.is_supervisor:
            raise ValidationError("An inactive employee cannot be a supervisor.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.employee_id:
            self.employee_id = f"HR-EMP-{date.today().year}-{uuid.uuid4().hex[:6]}".upper()

        super().save(*args, **kwargs)

        if self.is_supervisor:
            Department_Superior.objects.update_or_create(
                dept=self.dept,
                position=self.position,
                defaults={
                    'employee': self,
                    'is_archived': False
                }
            )
        else:
            Department_Superior.objects.filter(employee=self).update(is_archived=True)

        def __str__(self):
            return f"{self.first_name} {self.last_name} ({self.employee_id})"

    class Meta:
        db_table = 'employees'
