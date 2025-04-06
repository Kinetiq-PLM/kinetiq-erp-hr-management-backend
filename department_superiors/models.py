from django.db import models
from departments.models import Department
from employees.models import Employee
from positions.models import Position

class DepartmentSuperior(models.Model):
    dept = models.ForeignKey(Department, db_column='dept_id', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, db_column='employee_id', on_delete=models.CASCADE)
    position = models.ForeignKey(Position, db_column='position_id', on_delete=models.CASCADE)
    superior_job_title = models.CharField(max_length=100)
    hierarchy_level = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.dept.dept_id} - {self.employee.employee_id} - {self.superior_job_title}"

    class Meta:
        db_table = "department_superiors"
        unique_together = ('dept', 'employee')
