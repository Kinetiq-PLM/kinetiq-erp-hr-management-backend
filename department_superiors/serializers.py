from rest_framework import serializers
from .models import DepartmentSuperior

class DepartmentSuperiorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSuperior
        fields = '__all__'
        read_only_fields = ('dept_id', 'superior_job_title')
