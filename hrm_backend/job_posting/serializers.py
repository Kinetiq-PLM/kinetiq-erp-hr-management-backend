from rest_framework import serializers
from .models import (
    Job_Posting,
    Department,
)
from positions.models import Position  
from department_superiors.models import Department_Superior
from .models import Job_Posting
from departments.models import Department
from positions.models import Position
from django.db import connection
from decimal import Decimal

class Job_Posting_Serializer(serializers.ModelSerializer):
    dept_id = serializers.SerializerMethodField()
    position_id = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    finance_approval_id = serializers.SerializerMethodField()

    class Meta:
        model = Job_Posting
        fields = [
            'job_id',
            'dept_id',
            'position_id',
            'position_title',
            'description',
            'requirements',
            'employment_type',
            'base_salary',
            'daily_rate',
            'duration_days',
            'finance_approval_id',
            'finance_approval_status',
            'posting_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'job_id',
            'created_at',
            'updated_at',
            'finance_approval_id',
            'finance_approval_status',
            'posting_status',
        ]

    def get_dept_id(self, obj):
        return obj.dept.dept_id if obj.dept else None

    def get_position_id(self, obj):
        return obj.position.position_id if obj.position else None

    def get_position_title(self, obj):
        return obj.position.position_title if obj.position else None

    def get_finance_approval_id(self, obj):
        return obj.finance_approval.finance_approval_id if obj.finance_approval else None

class Job_Posting_CreateSerializer(serializers.ModelSerializer):
    dept_id = serializers.PrimaryKeyRelatedField(
        queryset = Department.objects.all(),
        source = 'dept'
    )
    position_id = serializers.PrimaryKeyRelatedField(
        queryset = Position.objects.all(),  
        source = 'position'
    )
    base_salary = serializers.DecimalField(max_digits = 10, decimal_places = 2, required = False, allow_null = True)
    daily_rate = serializers.DecimalField(max_digits = 10, decimal_places = 2, required = False, allow_null = True)
    duration_days = serializers.IntegerField(required = False, allow_null = True)
    
    class Meta:
        model = Job_Posting
        fields = [
            'dept_id',
            'position_id',
            'position_title',
            'description',
            'requirements',
            'employment_type',
            'base_salary',
            'daily_rate',
            'duration_days',
            'posting_status',
        ]
    
    def validate(self, data):
        employment_type = data.get('employment_type')
        base_salary = data.get('base_salary')
        daily_rate = data.get('daily_rate')
        duration_days = data.get('duration_days')
                
        if employment_type == 'Regular':
            if base_salary is None or (isinstance(base_salary, str) and not base_salary.strip()):
                raise serializers.ValidationError({"base_salary": ["Base salary is required for Regular positions"]})
            data['daily_rate'] = None
            data['duration_days'] = None
        elif employment_type == 'Contractual':
            if daily_rate is None or (isinstance(daily_rate, str) and not daily_rate.strip()):
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Contractual positions"]})
            data['base_salary'] = None
            if duration_days is None or duration_days < 30 or duration_days > 180:
                raise serializers.ValidationError({"duration_days": ["Contractual positions require duration between 30 and 180 days"]})
        elif employment_type == 'Seasonal':
            if daily_rate is None or (isinstance(daily_rate, str) and not daily_rate.strip()):
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Seasonal positions"]})
            data['base_salary'] = None
            if duration_days is None or duration_days < 1 or duration_days > 29:
                raise serializers.ValidationError({"duration_days": ["Seasonal positions require duration between 1 and 29 days"]})
        else:
            raise serializers.ValidationError({"employment_type": [f"Invalid employment type: {employment_type}. Must be Regular, Contractual, or Seasonal."]})
        
        if data.get('posting_status') is None:
            data['posting_status'] = 'Draft'
        
        required_fields = ['description', 'requirements']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise serializers.ValidationError({field: ["This field is required."] for field in missing_fields})
        
        return data       
    
    def create(self, validated_data):
        try:
            if not validated_data.get('job_id'):
                validated_data['job_id'] = Job_Posting.generate_job_id()
                
            if not validated_data.get('position_title') and validated_data.get('position'):
                validated_data['position_title'] = validated_data['position'].position_title
            
            print(f"Creating job posting with data: {validated_data}")
                
            return super().create(validated_data)
        except Exception as e:
            print(f"Error creating job posting: {str(e)}")
            raise serializers.ValidationError(f"Error creating job posting: {str(e)}")

    def update(self, instance, validated_data):
        try:
            print(f"Updating job posting with data: {validated_data}")
            
            dept = validated_data.pop('dept', None)
            if dept:
                instance.dept = dept
            
            position = validated_data.pop('position', None)
            if position:
                instance.position = position
                if not validated_data.get('position_title'):
                    instance.position_title = position.position_title
            
            employment_type = validated_data.get('employment_type', instance.employment_type)
            
            if employment_type == 'Regular':
                base_salary = validated_data.get('base_salary')
                if base_salary is not None:
                    instance.base_salary = base_salary
                    print(f"Setting base_salary to: {base_salary}")
                instance.daily_rate = None
                instance.duration_days = None
            elif employment_type in ['Contractual', 'Seasonal']:
                daily_rate = validated_data.get('daily_rate')
                if daily_rate is not None:
                    instance.daily_rate = daily_rate
                    print(f"Setting daily_rate to: {daily_rate}")
                instance.base_salary = None
                duration_days = validated_data.get('duration_days')
                if duration_days is not None:
                    instance.duration_days = duration_days
                    print(f"Setting duration_days to: {duration_days}")
            
            for attr, value in validated_data.items():
                if attr not in ['base_salary', 'daily_rate', 'duration_days']:
                    setattr(instance, attr, value)
            
            instance.save()
            instance.refresh_from_db()
            
            return instance
        except Exception as e:
            print(f"Error updating job posting: {str(e)}")
            raise serializers.ValidationError(f"Error updating job posting: {str(e)}")

class Job_Posting_RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Posting
        fields = [
            'position',
            'description',
            'requirements',
            'employment_type',
            'base_salary',
            'daily_rate',
            'duration_days',
            'posting_status',
        ]
    base_salary = serializers.DecimalField(max_digits = 10, decimal_places = 2, required = False, allow_null = True)
    daily_rate = serializers.DecimalField(max_digits = 10, decimal_places = 2, required = False, allow_null = True)
    duration_days = serializers.IntegerField(required = False, allow_null = True)
    def validate(self, data):
        employment_type = data.get('employment_type')
        base_salary = data.get('base_salary')
        daily_rate = data.get('daily_rate')
        duration_days = data.get('duration_days')
        
        if employment_type == 'Regular':
            if not base_salary:
                raise serializers.ValidationError({"base_salary": ["Base salary is required for Regular positions"]})
            data['daily_rate'] = None
            data['duration_days'] = None
        elif employment_type == 'Contractual':
            if not daily_rate:
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Contractual positions"]})
            data['base_salary'] = None
            if duration_days is None or duration_days < 30 or duration_days > 180:
                raise serializers.ValidationError({"duration_days": ["Contractual positions require duration between 30 and 180 days"]})
        elif employment_type == 'Seasonal':
            if not daily_rate:
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Seasonal positions"]})
            data['base_salary'] = None
            if duration_days is None or duration_days < 1 or duration_days > 29:
                raise serializers.ValidationError({"duration_days": ["Seasonal positions require duration between 1 and 29 days"]})
        else:
            raise serializers.ValidationError({"employment_type": [f"Invalid employment type: {employment_type}. Must be Regular, Contractual, or Seasonal."]})
        
        if data.get('posting_status') is None:
            data['posting_status'] = 'Draft'
            
        return data
    
    def create(self, validated_data):
        from uuid import uuid4
        request = self.context['request']
        
        try:
            dept_superior = Department_Superior.objects.get(user = request.user)
            validated_data['dept'] = dept_superior.department
        except Department_Superior.DoesNotExist:
            raise serializers.ValidationError("Requesting user is not a registered Department Superior.")

        validated_data['job_id'] = f"JOBREQ-{uuid4()}"
        validated_data['posting_status'] = 'Requested'
        
        return Job_Posting.objects.create(**validated_data)
    
