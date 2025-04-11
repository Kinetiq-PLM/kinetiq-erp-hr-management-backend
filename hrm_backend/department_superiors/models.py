from django.db import models
from django.apps import apps
from departments.models import Department
from positions.models import Position
from employees.models import Employee
class DepartmentSuperior(models.Model):
    dept_superior_id = models.AutoField(primary_key = True) # added and solved the isssue 
    dept = models.ForeignKey(Department, db_column = 'dept_id', on_delete=models.CASCADE)
    position = models.ForeignKey(Position, db_column = 'position_id', on_delete=models.CASCADE)
    hierarchy_level = models.PositiveIntegerField()
    is_archived = models.BooleanField(default = False) 
    class Meta:
        db_table = "department_superiors"
        unique_together = ('dept', 'position')

    def __str__(self):
        return f"{self.dept.dept_name} - {self.position.position_title}"

    # added new columns (that are not part of the table in department superiors)
    def get_employee(self):
        from employees.models import Employee
        return Employee.objects.filter(position=self.position, dept=self.dept).first()

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
