from .models import Department
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class Department_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['dept_id', 'dept_name', 'is_archived']

    # Validations
    def validate_dept_name(self, value):
        if Department.objects.filter(dept_name = value, is_archived = False).exists():
            raise ValidationError(f"Department name '{value}' already exists and is not archived.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep = {
            'dept_id': rep.get('dept_id'),
            'dept_name': rep.get('dept_name'),
            'is_archived': rep.get('is_archived'),
        }
        return rep
