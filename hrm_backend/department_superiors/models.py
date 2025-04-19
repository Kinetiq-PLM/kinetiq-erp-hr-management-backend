from django.apps import apps
from django.db import models
from departments.models import Department
from positions.models import Position  # This imports the Position model
from employees.models import Employee
from django.core.exceptions import ValidationError
import string
import random
from datetime import date

class Department_Superior(models.Model):
    dept_superior_id = models.CharField(
        primary_key = True,
        max_length = 50,
        editable = False,
        unique = True,
        default = ''
    )
    dept = models.ForeignKey(Department, db_column = 'dept_id', on_delete = models.CASCADE)
    
    # Updated this line to match the actual database structure
    # The 'Positions' referenced in the actual database (see models_updated.py)
    position = models.ForeignKey('positions.Position', db_column = 'position_id', on_delete = models.DO_NOTHING, blank=True, null=True)
    
    hierarchy_level = models.PositiveIntegerField()
    is_archived = models.BooleanField(default = False)
 
    # validation errors
    def clean(self):
        if Department_Superior.objects.filter(dept = self.dept, position = self.position, is_archived = False).exists():
            raise ValidationError(f"A department superior for {self.dept.dept_name} with the position {self.position.position_title} already exists and is active.")
        
    def generate_department_superior_id(self):
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
        return f"DEPT-SUPT-{date.today().year}-{random_part}"

    def save(self, *args, **kwargs):
        if not self.dept_superior_id:
            self.dept_superior_id = self.generate_department_superior_id()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "department_superiors"
        unique_together = ('dept', 'position')
        managed = False  # Removed semicolon which is not valid Python syntax
        verbose_name = "Department Superiors"
        verbose_name_plural = "Department Superiors"

    def __str__(self):
        return f"{self.dept.dept_name} - {self.position.position_title}" if self.position else f"{self.dept.dept_name} - No Position"

    def get_employee(self):
        Employee = apps.get_model('employees', 'Employee')
        return Employee.objects.filter(position = self.position, dept = self.dept).first()

    def get_employee_id(self):
        emp = self.get_employee()
        return emp.employee_id if emp else None

    def get_first_name(self):
        emp = self.get_employee()
        return emp.first_name if emp else None

    def get_last_name(self):
        emp = self.get_employee()
        return emp.last_name if emp else None

    def get_phone(self):
        emp = self.get_employee()
        return emp.phone if emp else None

    def get_employee_status(self):
        emp = self.get_employee()
        return emp.status if emp else None