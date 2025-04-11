from .models import Department
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class Department_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['dept_id', 'dept_name', 'is_archived']

# validations 
    def validate_dept_name(self, value):
        if Department.objects.filter(dept_name = value, is_archived = False).exists():
            raise ValidationError(f"Department name '{value}' already exists and is not archived.")
        return value
    
# for history, although just specific departments not over all history of departemnts
class Department_History_Serializer(serializers.ModelSerializer):
    history_user = serializers.CharField(source="history_user.username", read_only = True)
    history_change_reason = serializers.CharField(read_only = True)
    history_date = serializers.DateTimeField(read_only = True)
    status = serializers.SerializerMethodField()
    dept_name = serializers.CharField(source='dept.dept_name', read_only = True)

    class Meta:
        model = Department.history.model
        fields = ['history_user', 'history_change_reason', 'history_date', 'status', 'dept_name']

    def get_status(self, obj):
        if obj.history_change_reason:
            return "Changed"
        else:
            return "Unchanged"