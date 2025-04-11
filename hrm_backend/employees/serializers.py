from rest_framework import serializers
from .models import Employee

class Employee_Serializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only = True)
    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'user_id',
            'dept_id',
            'position_id',
            'first_name',
            'last_name',
            'email',  # ewan ko kung paano to, hindi raw sa atin to eh
            'phone',
            'employment_type',
            'status',
            'reports_to',
            'is_supervisor',
            'created_at',
            'updated_at',
            'is_archived',
        ]
        read_only_fields = [
            'employee_id',
            'user_id',
            'dept_id',
            'position_id',
            'email',
            'salary_grade',
            'created_at',
            'updated_at',
        ]


# for history, although just specific departments not over all history of departemnts
class Employee_History_Serializer(serializers.ModelSerializer):
    history_user = serializers.CharField(source="history_user.username", read_only = True)
    history_change_reason = serializers.CharField(read_only = True)
    history_date = serializers.DateTimeField(read_only = True)
    status = serializers.SerializerMethodField()
    dept_name = serializers.CharField(source='dept.dept_name', read_only = True)

    class Meta:
        model = Employee.history.model
        fields = ['history_user', 'history_change_reason', 'history_date', 'status', 'dept_name']

    def get_status(self, obj):
        if obj.history_change_reason:
            return "Changed"
        else:
            return "Unchanged"