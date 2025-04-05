from django.db import models
from dateutil.relativedelta import relativedelta
from employees.models import Employee


class EmployeeSalary(models.Model):
    salary_id = models.CharField(primary_key = True, max_length = 50)
    employee = models.ForeignKey(Employee, to_field = 'employee_id', db_column = 'employee_id', on_delete=models.DO_NOTHING)
    base_salary = models.DecimalField(max_digits = 10, decimal_places=2, null = True, blank = True)
    daily_rate = models.DecimalField(max_digits = 10, decimal_places=2, null = True, blank = True)
    contract_start_date = models.DateField(null = True, blank = True)
    contract_end_date = models.DateField(null = True, blank = True)
    effective_date = models.DateField(auto_now_add = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'employee_salary'
        managed = True
        unique_together = ('employee', 'effective_date')

    def save(self, *args, **kwargs):
        if self.employee and self.contract_start_date and not self.contract_end_date:
            self.contract_end_date = self.contract_start_date + relativedelta(months=6)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.salary_id} - {self.employee.employee_id if self.employee else 'No Employee'}"
