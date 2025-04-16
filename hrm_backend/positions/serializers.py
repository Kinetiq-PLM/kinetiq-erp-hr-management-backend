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
        read_only_fields = ('created_at', 'updated_at')

class Position_CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = [
            'position_title',
            'salary_grade',
            'min_salary',
            'max_salary',
            'employment_type',
            'typical_duration_days',
            'is_active',
            'is_archived'
        ]
