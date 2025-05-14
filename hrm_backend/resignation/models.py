from django.db import models
import uuid

class Resignation(models.Model):
    resignation_id = models.CharField(max_length = 255, primary_key = True, default = uuid.uuid4, editable = False)
    employee = models.ForeignKey('employees.Employee', models.DO_NOTHING, blank = True, null = True)
    submission_date = models.DateTimeField(blank = True, null = True)
    notice_period_days = models.IntegerField(blank = True, null = True)
    clearance_status = models.CharField(max_length = 20, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    documents = models.JSONField(blank = True, null = True)
    reason = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.resignation_id
    
    class Meta:
        db_table = "resignations"
        managed = False
