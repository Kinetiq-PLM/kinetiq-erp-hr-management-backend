from django.db import models
from django.utils import timezone
from employees.models import Employee 
from django.core.exceptions import ValidationError
import uuid

class Employee_Leave_Balance(models.Model):
    balance_id = models.CharField(max_length = 255, primary_key = True)
    employee = models.ForeignKey('employees.Employee', on_delete = models.CASCADE)
    year = models.IntegerField(default = timezone.now().year)
    sick_leave_remaining = models.IntegerField(default = 15)
    vacation_leave_remaining = models.IntegerField(default = 15)
    maternity_leave_remaining = models.IntegerField(default = 105)
    paternity_leave_remaining = models.IntegerField(default = 7)
    solo_parent_leave_remaining = models.IntegerField(default = 7)
    unpaid_leave_taken = models.IntegerField(default = 0)

    def __str__(self):
        return f"Leave Balance for {self.employee.employee_id} ({self.year})"
    
    def generate_balance_id():
        year = timezone.now().year
        unique_part = str(uuid.uuid4().int)[:3].upper()
        return f"LB-{year}-{unique_part}"

    class Meta:
        db_table = "employee_leave_balances"
        verbose_name = "Employee Leave Balance"
        verbose_name_plural = "Employee Leave Balances"

    def update_leave_balance(self, leave_request):
        leave_type = leave_request.leave_type
        total_days = leave_request.total_days
        
        if leave_type == "Sick":
            if self.sick_leave >= total_days:
                self.sick_leave -= total_days
            else:
                raise ValidationError("Insufficient sick leave balance.")
        elif leave_type == "Vacation":
            if self.vacation_leave >= total_days:
                self.vacation_leave -= total_days
            else:
                raise ValidationError("Insufficient vacation leave balance.")
        elif leave_type == "Emergency":
            if self.emergency_leave >= total_days:
                self.emergency_leave -= total_days
            else:
                raise ValidationError("Insufficient emergency leave balance.")
        
        self.save()

    def calculate_total_leave_days(self):
        self.total_leave_days = self.sick_leave + self.vacation_leave + self.emergency_leave
        self.save()

    def approve_leave(self):
        if self.status == "Approved":
            leave_balance = self.employee.leave_balance
            leave_balance.update_leave_balance(self)
            leave_balance.calculate_total_leave_days()
