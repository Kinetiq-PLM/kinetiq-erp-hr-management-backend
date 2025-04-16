from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
import uuid

class Position(models.Model):
    EMPLOYMENT_TYPES = [
        ('Regular', 'Regular'),
        ('Contractual', 'Contractual'),
        ('Seasonal', 'Seasonal'),
    ]

    position_id = models.CharField(max_length = 255, primary_key = True, editable = False, unique = True)
    position_title = models.CharField(max_length = 100)
    salary_grade = models.CharField(max_length = 20, blank = True, null = True)
    min_salary = models.DecimalField(max_digits = 10, decimal_places = 2)
    max_salary = models.DecimalField(max_digits = 10, decimal_places = 2)
    employment_type = models.CharField(max_length = 20, choices = EMPLOYMENT_TYPES)
    typical_duration_days = models.PositiveSmallIntegerField(blank = True, null = True)
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False)
    
    # validation errors
    def clean(self):
        if Position.objects.filter(position_title = self.position_title, is_archived = False).exists():
            raise ValidationError(f"A position title with the name '{self.position_title}' already exists and is active.")

    def save(self, *args, **kwargs):
        if not self.position_id:
            prefix = {
                'Regular': 'REG',
                'Contractual': 'CTR',
                'Seasonal': 'SEA'
            }.get(self.employment_type, 'POS')
            self.position_id = f"{prefix}-{date.today().strftime('%y%m')}-{uuid.uuid4().hex[:4]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.position_title} ({self.employment_type})"

    class Meta:
        db_table = 'positions'
