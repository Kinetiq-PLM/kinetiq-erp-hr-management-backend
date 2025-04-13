from django.apps import apps
from django.db import models
from departments.models import Department
from positions.models import Position
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
import string
import random
from datetime import date

class Department_Superior(models.Model):
    dept_superior_id = models.CharField(
        primary_key = True,
        max_length = 50,
        editable = False,
        unique = True,
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null = True,
        blank = True
    )

    dept = models.ForeignKey(Department, db_column = 'dept_id', on_delete = models.CASCADE)
    position = models.ForeignKey(Position, db_column = 'position_id', on_delete = models.CASCADE)
    hierarchy_level = models.PositiveIntegerField()
    is_archived = models.BooleanField(default = False)

    history = HistoricalRecords()
    change_reason = models.CharField(max_length = 255, blank = True, null = True)

    # validation errors
    def clean(self):
        if not self.is_archived:
            existing = Department_Superior.objects.filter(
                dept = self.dept,
                position = self.position,
                is_archived = False
            )
            if self.pk:
                existing = existing.exclude(pk = self.pk)
            if existing.count() >= 3:
                raise ValidationError("Maximum of 3 active supervisors allowed per department and position.")
        
    def generate_department_superior_id(self):
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
        return f"DEPT-SUPT-{date.today().year}-{random_part}"

    def save(self, *args, **kwargs):
        if not self.dept_superior_id:
            self.dept_superior_id = self.generate_department_superior_id()
            
        super().save(*args, **kwargs)

    class Meta:
        db_table = "department_superiors"
        verbose_name = "Department Superiors" # added para maganda tignan sa admin
        verbose_name_plural = "Department Superiors"

    def __str__(self):
        return f"{self.dept.dept_name} - {self.position.position_title} - {self.get_superior_name()}"   
    
    def get_superior_name(self):
        return f"{self.employee.first_name} {self.employee.last_name}" if self.employee else "No Assigned Employee"

    def get_employee_id(self):
        return self.employee.employee_id if self.employee else None
    
    def get_first_name(self):
        return self.employee.first_name if self.employee else None

    def get_last_name(self):
        return self.employee.last_name if self.employee else None

    def get_phone(self):
        return self.employee.phone if self.employee else None

    def get_employee_status(self):
        return self.employee.status if self.employee else None
