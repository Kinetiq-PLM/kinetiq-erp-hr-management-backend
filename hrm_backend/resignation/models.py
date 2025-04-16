from django.db import models
import uuid

class Resignation(models.Model):
    resignation_id = models.CharField(max_length = 255, primary_key = True, default = uuid.uuid4, editable = False)
    employee_id = models.CharField(max_length = 255)
    submission_date = models.DateTimeField(auto_now_add = True)
    notice_period_days = models.IntegerField()
    hr_approver_id = models.CharField(max_length = 255, null = True, blank = True)
    approval_status = models.CharField(max_length = 20, default = 'Pending')
    clearance_status = models.CharField(max_length = 20, default = 'Pending')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.resignation_id
