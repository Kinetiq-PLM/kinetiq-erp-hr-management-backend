from rest_framework import serializers
from .models import Employee_Leave_Request

class Employee_Leave_Request_HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee_Leave_Request
        fields = [
            'leave_id',
            'employee',
            'immediate_superior_id',
            'management_approval_id',
            'leave_type',
            'start_date',
            'end_date',
            'status',
            'is_paid',
        ]
        read_only_fields = ['status']  # Optional

class Department_Superior_History_Serializer(serializers.ModelSerializer):
    history_user = serializers.CharField(source="history_user.username", read_only = True)
    history_change_reason = serializers.CharField(read_only = True)
    history_date = serializers.DateTimeField(read_only = True)
    status = serializers.SerializerMethodField()
    dept_name = serializers.CharField(source='dept.dept_name', read_only = True)

    class Meta:
        model = Employee_Leave_Request.history.model
        fields = ['history_user', 'history_change_reason', 'history_date', 'status', 'dept_name']

    def get_status(self, obj):
        if obj.history_change_reason:
            return "Changed"
        else:
            return "Unchanged"
