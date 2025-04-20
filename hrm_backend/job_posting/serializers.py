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
        queryset=Department.objects.all(),
        source='dept'
    )
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),  
        source='position'
    )
    
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
        """
        Enhanced validation with better error messages
        """
        # Get employment type
        employment_type = data.get('employment_type')
        base_salary = data.get('base_salary')
        daily_rate = data.get('daily_rate')
        duration_days = data.get('duration_days')
        
        # Print for debugging - remove in production
        print(f"Validating job posting: employment_type={employment_type}, base_salary={base_salary}, daily_rate={daily_rate}, duration_days={duration_days}")
        
        # Enforce compensation rules based on employment type
        if employment_type == 'Regular':
            if not base_salary:
                raise serializers.ValidationError({"base_salary": ["Base salary is required for Regular positions"]})
            # Set daily_rate to NULL for Regular employees
            data['daily_rate'] = None
            # For Regular positions, duration_days must be NULL
            data['duration_days'] = None
        elif employment_type == 'Contractual':
            if not daily_rate:
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Contractual positions"]})
            # Set base_salary to NULL for Contractual employees
            data['base_salary'] = None
            # Validate duration_days for Contractual (30-180 days)
            if duration_days is None or duration_days < 30 or duration_days > 180:
                raise serializers.ValidationError({"duration_days": ["Contractual positions require duration between 30 and 180 days"]})
        elif employment_type == 'Seasonal':
            if not daily_rate:
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Seasonal positions"]})
            # Set base_salary to NULL for Seasonal employees
            data['base_salary'] = None
            # Validate duration_days for Seasonal (1-29 days)
            if duration_days is None or duration_days < 1 or duration_days > 29:
                raise serializers.ValidationError({"duration_days": ["Seasonal positions require duration between 1 and 29 days"]})
        else:
            # If someone sends an invalid employment type
            raise serializers.ValidationError({"employment_type": [f"Invalid employment type: {employment_type}. Must be Regular, Contractual, or Seasonal."]})
        
        # Ensure posting_status has a default value
        if data.get('posting_status') is None:
            data['posting_status'] = 'Draft'
        
        # Validate required fields
        required_fields = ['description', 'requirements']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise serializers.ValidationError({field: ["This field is required."] for field in missing_fields})
        
        return data        
    def create(self, validated_data):
        """
        Enhanced create method with error handling
        """
        try:
            # Generate job ID if not provided
            if not validated_data.get('job_id'):
                validated_data['job_id'] = Job_Posting.generate_job_id()
                
            # Ensure position_title is set if not provided
            if not validated_data.get('position_title') and validated_data.get('position'):
                validated_data['position_title'] = validated_data['position'].position_title
            
            # Print for debugging - remove in production
            print(f"Creating job posting with data: {validated_data}")
                
            return super().create(validated_data)
        except Exception as e:
            # Log the error - in production you'd use a proper logger
            print(f"Error creating job posting: {str(e)}")
            raise serializers.ValidationError(f"Error creating job posting: {str(e)}")
           
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

    def validate(self, data):
        """
        Validate data according to employment type constraints
        """
        employment_type = data.get('employment_type')
        base_salary = data.get('base_salary')
        daily_rate = data.get('daily_rate')
        duration_days = data.get('duration_days')
        
        # Enforce compensation rules based on employment type
        if employment_type == 'Regular':
            if not base_salary:
                raise serializers.ValidationError({"base_salary": ["Base salary is required for Regular positions"]})
            # Set daily_rate to None for Regular employees
            data['daily_rate'] = None
            # For Regular positions, duration_days must be NULL
            data['duration_days'] = None
        elif employment_type == 'Contractual':
            if not daily_rate:
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Contractual positions"]})
            # Set base_salary to None for Contractual employees
            data['base_salary'] = None
            # Validate duration_days for Contractual (30-180 days)
            if duration_days is None or duration_days < 30 or duration_days > 180:
                raise serializers.ValidationError({"duration_days": ["Contractual positions require duration between 30 and 180 days"]})
        elif employment_type == 'Seasonal':
            if not daily_rate:
                raise serializers.ValidationError({"daily_rate": ["Daily rate is required for Seasonal positions"]})
            # Set base_salary to None for Seasonal employees
            data['base_salary'] = None
            # Validate duration_days for Seasonal (1-29 days)
            if duration_days is None or duration_days < 1 or duration_days > 29:
                raise serializers.ValidationError({"duration_days": ["Seasonal positions require duration between 1 and 29 days"]})
        else:
            # If someone sends an invalid employment type
            raise serializers.ValidationError({"employment_type": [f"Invalid employment type: {employment_type}. Must be Regular, Contractual, or Seasonal."]})
        
        # Ensure posting_status has a default value if not provided
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
    
