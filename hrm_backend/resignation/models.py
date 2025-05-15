from django.db import models
from employees.models import Employee
import uuid

class Resignation(models.Model):
    resignation_id = models.CharField(max_length = 255, primary_key = True, default = uuid.uuid4, editable = False)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)
    # employee_id = models.CharField(max_length = 255, unique = True)
    submission_date = models.DateTimeField(auto_now_add = True)
    notice_period_days = models.IntegerField()
    # approval_status = models.CharField(max_length = 20, default = 'Pending')
    clearance_status = models.CharField(max_length = 20, default = 'Pending')
    reason = models.TextField(null = True, blank = True)
    documents = models.JSONField(null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    documents = models.JSONField(blank = True, null = True)
    reason = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.resignation_id
    
    class Meta:
        db_table = "resignations"
        managed = False
