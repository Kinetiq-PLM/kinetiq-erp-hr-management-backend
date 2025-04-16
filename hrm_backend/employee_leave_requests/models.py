from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import random
import string

class Employee_Leave_Request(models.Model):
    leave_id = models.CharField(max_length = 255, primary_key = True, editable = False)
    employee = models.ForeignKey('employees.Employee', on_delete = models.CASCADE)
    dept = models.ForeignKey('departments.Department', db_column='dept_id', on_delete = models.CASCADE)
    immediate_superior = models.ForeignKey("department_superiors.Department_Superior", on_delete = models.SET_NULL, null = True, blank = True, related_name = "approved_leaves")
    management_approval = models.ForeignKey("department_superiors.Department_Superior", on_delete = models.SET_NULL, null = True, blank = True, related_name = "management_approved_leaves")
    leave_type = models.CharField(max_length = 20, choices=[('Sick', 'Sick'), ('Vacation', 'Vacation'), ('Emergency', 'Emergency')])
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    is_paid = models.BooleanField(default = True)
    status = models.CharField(max_length = 50, default = "Pending", choices = [("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")])
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False)

    created_at = models.DateTimeField(default = timezone.now)

    def clean(self):
        if Employee_Leave_Request.objects.filter(
            employee = self.employee,
            status = "Pending",
            start_date__lte = self.end_date,
            end_date__gte = self.start_date
        ).exists():
            raise ValidationError("An active leave request already exists for these dates.")

        if self.start_date < timezone.now().date():
            raise ValidationError("Leave request start date cannot be in the past.")

        if not self.leave_type:
            raise ValidationError("Leave type is required.")

    def generate_leave_id(self):
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 3))
        return f"LV-2025-{random_part}"

    def save(self, *args, **kwargs):
        if not self.leave_id:
            self.leave_id = self.generate_leave_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} Leave ({self.leave_type}) from {self.start_date} to {self.end_date}"

    class Meta:
            db_table = "leave_requests"
            verbose_name = "Employee Leave Request"
            verbose_name_plural = "Employee Leave Requests"