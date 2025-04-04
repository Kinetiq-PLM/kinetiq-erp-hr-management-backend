from rest_framework import serializers
from .models import EmployeeSalary

class EmployeeSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalary
        fields = '__all__'

    def validate(self, data):
        emp_type = data.get('employment_type')

        if emp_type == 'regular':
            if not data.get('base_salary'):
                raise serializers.ValidationError("Base salary is required for regular employees.")
            data['daily_rate'] = None
            data['contract_start_date'] = None
            data['contract_end_date'] = None

        elif emp_type in ['contractual', 'seasonal']:
            if not data.get('daily_rate') or not data.get('contract_start_date'):
                raise serializers.ValidationError("Daily rate and contract start date are required for contractual or seasonal employment.")
            data['base_salary'] = None

        return data
