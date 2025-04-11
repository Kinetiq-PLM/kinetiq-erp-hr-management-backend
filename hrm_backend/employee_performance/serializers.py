from rest_framework import serializers
from .models import EmployeePerformance

class EmployeePerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePerformance
        fields = '__all__'
