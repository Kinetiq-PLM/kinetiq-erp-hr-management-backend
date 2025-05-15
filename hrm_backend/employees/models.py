from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from departments.models import Department
from positions.models import Position
from django.core.exceptions import ValidationError
from datetime import date
import uuid
import re
from employees.card_utils import get_id_card_photo

User = get_user_model()

# Validate image size and type (JPEG, PNG)
def validate_image(image):
    if image.file.size > 2 * 1024 * 1024:
        raise ValidationError('Image file too large ( > 2mb )')
    
    extension = image.file.name.split('.')[-1].lower()
    if extension not in ['jpg', 'jpeg', 'png']:
        raise ValidationError('Image file type not supported. Only JPEG and PNG files are accepted.')

class Employee(models.Model):
    EMPLOYMENT_TYPES = [
        ('Regular', 'Regular'),
        ('Contractual', 'Contractual'),
        ('Seasonal', 'Seasonal'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Terminated', 'Terminated'),
        ('Resigned', 'Resigned'),
    ]

    employee_id = models.CharField(
        max_length=255,
        primary_key=True,
        editable=False,
        unique=True,
    )
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    is_supervisor = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    # New fields from the OTHER code
    photo = models.ImageField(upload_to='employee_photos', validators=[validate_image])
    id_card_photo = models.ImageField(upload_to='employee_id_cards', blank=True, null=True)

    # Validation methods
    def clean(self):
        phone_regex = re.compile(r'^[\d\+\-\(\)\s]*$')
        if not phone_regex.match(self.phone):
            raise ValidationError(f"Phone number '{self.phone}' is invalid. Only numbers and valid characters are allowed.")
        
        name_regex = re.compile(r'^[A-Za-z\s\'-]+$')
        if not name_regex.match(self.first_name):
            raise ValidationError(f"First name '{self.first_name}' contains invalid characters. Only letters and basic punctuation are allowed.")
        if not name_regex.match(self.last_name):
            raise ValidationError(f"Last name '{self.last_name}' contains invalid characters. Only letters and basic punctuation are allowed.")
        
        if Employee.objects.filter(phone=self.phone, is_archived=False).exclude(pk=self.pk).exists():
            raise ValidationError(f"An active employee with the phone number '{self.phone}' already exists.")
        
        if Employee.objects.filter(first_name=self.first_name, last_name=self.last_name, is_archived=False).exclude(pk=self.pk).exists():
            raise ValidationError(f"An active employee with the name '{self.first_name} {self.last_name}' already exists.")
        
        if self.status == 'Inactive' and self.is_supervisor:
            raise ValidationError("An inactive employee cannot be a supervisor.")

    def save(self, *args, **kwargs):
        # Check if this is a new record that needs an ID card
        if self.photo:  # Only proceed if a photo was uploaded
            # Remove previous photo if it exists
            if self.id_card_photo:
                self.id_card_photo.delete(save=False)
                
            # Add id_card_photo to the instance
            try:
                self.id_card_photo.save(
                    f'{self.first_name}_{self.last_name}_id_card.jpg',
                    get_id_card_photo(self),
                    save=False
                )
            except Exception as e:
                # Log the error but don't prevent saving the employee
                print(f"Error generating ID card: {e}")
                # Optionally raise the error if you want to prevent saving without ID card
                # raise
    
        super().save(*args, **kwargs)

    def __str__(self):
        position_title = self.position.position_title if self.position else "No Position"
        return f"{self.first_name} {self.last_name} - {position_title}"

    class Meta:
        db_table = 'employees'
