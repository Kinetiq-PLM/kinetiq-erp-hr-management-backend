from rest_framework import serializers
from .models import LeaveRequest

class Employee_Leave_Request_HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['leave_id', 'created_at', 'updated_at']
