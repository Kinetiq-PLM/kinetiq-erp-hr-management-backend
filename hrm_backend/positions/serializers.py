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
    
    def validate(self, data):
        """
        Validate position data based on employment type
        """
        employment_type = data.get('employment_type')
        min_salary = data.get('min_salary')
        max_salary = data.get('max_salary')
        typical_duration_days = data.get('typical_duration_days')
        
        if employment_type == 'Regular':
            if min_salary < 0:
                raise serializers.ValidationError({"min_salary": "Minimum salary cannot be negative for Regular positions."})
            if typical_duration_days is not None:
                raise serializers.ValidationError({"typical_duration_days": "Regular positions should not have a duration specified."})
                
        elif employment_type in ['Contractual', 'Seasonal']:
            if min_salary < 500 or min_salary > 10000:
                raise serializers.ValidationError({"min_salary": "Minimum salary must be between 500 and 10,000 for non-Regular positions."})
                
            if employment_type == 'Contractual':
                if not typical_duration_days or typical_duration_days < 30 or typical_duration_days > 180:
                    raise serializers.ValidationError({"typical_duration_days": "Contractual positions must have duration between 30 and 180 days."})
            else:  # Seasonal
                if not typical_duration_days or typical_duration_days < 1 or typical_duration_days > 29:
                    raise serializers.ValidationError({"typical_duration_days": "Seasonal positions must have duration between 1 and 29 days."})
        
        if max_salary < min_salary:
            raise serializers.ValidationError({"max_salary": "Maximum salary must be greater than or equal to minimum salary."})
            
        return data