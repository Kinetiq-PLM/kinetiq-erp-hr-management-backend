from django.apps import apps
from django.db import models
from departments.models import Department
from positions.models import Position
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords

class Department_Superior(models.Model):
    dept_superior_id = models.CharField(primary_key = True)
    dept = models.ForeignKey(Department, db_column = 'dept_id', on_delete = models.CASCADE)
    position = models.ForeignKey(Position, db_column = 'position_id', on_delete = models.CASCADE)
    hierarchy_level = models.PositiveIntegerField()
    is_archived = models.BooleanField(default = False)

    history = HistoricalRecords() # history
    change_reason = models.CharField(max_length = 255, blank = True, null = True)


    # validation errors
    def clean(self):
        if Department_Superior.objects.filter(dept=self.dept, position=self.position, is_archived=False).exists():
            raise ValidationError(f"A department superior for {self.dept.dept_name} with the position {self.position.position_title} already exists and is active.")


    class Meta:
        db_table = "department_superiors"
        unique_together = ('dept', 'position')
        verbose_name = "Department Superiors" # added para maganda tignan sa admin
        verbose_name_plural = "Department Superiors"

    def __str__(self):
        return f"{self.dept.dept_name} - {self.position.position_title}"

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
