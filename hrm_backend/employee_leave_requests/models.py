from django.db import models
from django.utils import timezone
from .models import (
    Department,
    Department_Superior,
    Employee
)
import uuid

class LeaveRequest(models.Model):
    leave_id = models.CharField(max_length=255, primary_key = True)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
    dept = models.ForeignKey(Department, db_column='dept_id', on_delete = models.CASCADE)
    immediate_superior = models.ForeignKey(Department_Superior, on_delete = models.SET_NULL, null = True, blank = True, related_name = "approved_leaves")
    # management_approval = models.ForeignKey("DepartmentSuperior", on_delete = models.SET_NULL, null = True, blank = True, related_name = "management_approved_leaves")
    
    leave_type = models.CharField(max_length = 20, choices=[('Sick', 'Sick'), ('Vacation', 'Vacation'), ('Emergency', 'Emergency')])
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    is_paid = models.BooleanField(default = True)
    
    status = models.CharField(max_length = 50, default = "Pending", choices = [("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")])
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"{self.employee} Leave ({self.leave_type}) from {self.start_date} to {self.end_date}"
