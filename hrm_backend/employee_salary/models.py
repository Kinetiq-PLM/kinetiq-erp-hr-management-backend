from django.db import models
from dateutil.relativedelta import relativedelta
from datetime import date
from employees.models import Employee
import uuid

class Employee_Salary(models.Model):
    salary_id = models.CharField(primary_key = True, max_length = 50)
    employee = models.ForeignKey(Employee, to_field = 'employee_id', db_column = 'employee_id', on_delete = models.DO_NOTHING)
    base_salary = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    daily_rate = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    effective_date = models.DateField(auto_now_add = True)
    
    class Meta:
        db_table = 'employee_salary'
        managed = True
        unique_together = ('employee', 'effective_date')
        verbose_name = "Employee Salary" # added para maganda tignan sa admin
        verbose_name_plural = "Employee Salary"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new and not self.employee_id:
            self.employee_id = f"HR-EMP-{date.today().year}-{uuid.uuid4().hex[:6]}".upper()

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.salary_id} - {self.employee.employee_id if self.employee else 'No Employee'}"
