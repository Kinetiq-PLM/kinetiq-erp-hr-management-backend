from django.db import models
import uuid

class Department(models.Model):
    dept_id = models.CharField(primary_key = True, max_length = 20, editable = False)
    dept_name = models.CharField(max_length = 100, unique = True)

    def save(self, *args, **kwargs):
        if not self.dept_id:
            self.dept_id = f"HR-DEPT-2025-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.dept_name

    class Meta:
        db_table = "departments"
