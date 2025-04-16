from django.db import models
from django.core.exceptions import ValidationError
import uuid

class Department(models.Model):
    dept_id = models.CharField(primary_key = True, max_length = 20, editable = False)
    dept_name = models.CharField(max_length = 100)
    is_archived = models.BooleanField(default = False)

    # validation errors
    def clean(self):
        if Department.objects.filter(dept_name = self.dept_name, is_archived = False).exists():
            raise ValidationError(f"A department with the name '{self.dept_name}' already exists and is active.")

    def save(self, *args, **kwargs):
        if not self.dept_id:
            self.dept_id = f"HR-DEPT-2025-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.dept_name

    class Meta:
        db_table = "departments"
        indexes = [
            models.Index(fields=['dept_name'], name = 'unique_active_dept_name', condition = models.Q(is_archived = False))
        ]