from rest_framework import serializers
from .models import Position

class Position_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = [
            'position_id',
            'position_title',
            'salary_grade',
            'min_salary',
            'max_salary', 
            'employment_type',
            'typical_duration_days', 
            'is_active',
            'created_at', 
            'updated_at',
            'is_archived',
        ]
        read_only_fields = ('position_id', 'created_at', 'updated_at')


# for history, although just specific departments not over all history of departemnts
class Position_History_Serializer(serializers.ModelSerializer):
    history_user = serializers.CharField(source = "history_user.username", read_only = True)
    history_change_reason = serializers.CharField(read_only = True)
    history_date = serializers.DateTimeField(read_only = True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Position.history.model
        fields = ['history_user', 'history_change_reason', 'history_date', 'status']

    def get_status(self, obj):
        change_reason = obj.history_change_reason

        if "salary_grade" in change_reason:
            return "Salary grade changed"
        elif "min_salary" in change_reason or "max_salary" in change_reason:
            return "Salary details updated"
        elif "position_title" in change_reason:
            return "Position title updated"
        elif "employment_type" in change_reason:
            return "Employment type modified"

        if change_reason:
            return "General change"
        return "Unchanged"