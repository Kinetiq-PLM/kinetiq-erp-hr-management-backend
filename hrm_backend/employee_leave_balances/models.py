from django.db import models
from django.utils import timezone
import uuid

class Employee_Leave_Balance(models.Model):
    balance_id = models.CharField(max_length = 255, primary_key = True)
    employee_id = models.CharField(max_length = 255)
    year = models.IntegerField(default = timezone.now().year)
    sick_leave_remaining = models.IntegerField(default = 15)
    vacation_leave_remaining = models.IntegerField(default = 15)
    maternity_leave_remaining = models.IntegerField(default = 105)
    paternity_leave_remaining = models.IntegerField(default = 7)
    solo_parent_leave_remaining = models.IntegerField(default = 7)
    unpaid_leave_taken = models.IntegerField(default = 0)

    def __str__(self):
        return f"Leave Balance for {self.employee_id} ({self.year})"
    
    def generate_balance_id():
        year = timezone.now().year
        unique_part = str(uuid.uuid4().int)[:3].upper()
        return f"LB-{year}-{unique_part}"

    class Meta:
        db_table = "employee_leave_balances"
        verbose_name = "Employee Leave Balance"
        verbose_name_plural = "Employee Leave Balances"
