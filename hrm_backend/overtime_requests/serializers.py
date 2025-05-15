from .models import Overtime_Requests
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class Overtime_Requests_Serializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = Overtime_Requests
        fields = [
            'request_id',
            'employee_id',
            'employee_name',
            'request_date',
            'overtime_hours',
            'reason',
            'status',
            'approved_by',
            'approval_date',
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
        
    # Validations

    def validate_overtime_hours(self, value):
        if value <= 0:
            raise ValidationError("Overtime hours must be a positive number.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep = {
            'request_id': rep.get('request_id'),
            'employee_id': rep.get('employee_id'),
            'employee_name': rep.get('employee_name'),
            'request_date': rep.get('request_date'),
            'overtime_hours': rep.get('overtime_hours'),
            'reason': rep.get('reason'),
            'status': rep.get('status'),
            'approved_by': rep.get('approved_by'),
            'approval_date': rep.get('approval_date'),
        }
        return rep
