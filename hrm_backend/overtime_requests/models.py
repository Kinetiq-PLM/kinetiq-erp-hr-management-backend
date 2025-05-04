from django.db import models
from employees.models import Employee

class Overtime_Requests(models.Model):
    request_id = models.CharField(primary_key = True, max_length = 50)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
    request_date = models.DateField()
    overtime_hours = models.DecimalField(max_digits = 5, decimal_places = 2)
    reason = models.TextField()
    status = models.CharField(max_length = 20)
    approved_by = models.CharField(max_length = 10, blank = True, null = True)
    approval_date = models.DateField(blank = True, null = True)

    class Meta:
        db_table = 'overtime_requests'
        ordering = ['-request_date']

    def __str__(self):
        return f"Overtime Request {self.request_id} - {self.employee_id}"
