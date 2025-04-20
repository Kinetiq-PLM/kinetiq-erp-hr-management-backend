from rest_framework import serializers
from .models import Employee_Leave_Request
from employees.models import Employee
from django.utils import timezone
from datetime import datetime

class Employee_Leave_Request_Serializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.SerializerMethodField()
    immediate_superior_name = serializers.SerializerMethodField()
    management_approval_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee_Leave_Request
        fields = [
            'leave_id',
            'employee_id',
            'employee_name',
            'immediate_superior_id',
            'immediate_superior_name',
            'management_approval_id',
            'management_approval_name',
            'leave_type',
            'start_date',
            'end_date',
            'total_days',
            'is_paid',
            'status',
            'created_at',
            'updated_at',
            'is_archived',
        ]
        read_only_fields = ['status']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_immediate_superior_name(self, obj):
        if obj.immediate_superior_id:
            try:
                superior = Employee.objects.get(employee_id=obj.immediate_superior_id)
                return f"{superior.first_name} {superior.last_name}"
            except Employee.DoesNotExist:
                return "N/A"
        return "N/A"

    def get_management_approval_name(self, obj):
        if obj.management_approval_id:
            try:
                management_approval = Employee.objects.get(employee_id=obj.management_approval_id)
                return f"{management_approval.first_name} {management_approval.last_name}"
            except Employee.DoesNotExist:
                return "N/A"
        return "N/A"

class Employee_Leave_Request_CreateSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(write_only=True, required=False)  # Make it optional for PATCH
    immediate_superior_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True)
    management_approval_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True)

    class Meta:
        model = Employee_Leave_Request
        fields = [
            'employee_id',
            'immediate_superior_id',
            'management_approval_id',
            'leave_type',
            'start_date',
            'end_date',
            'is_paid',
            'status',
        ]

    def validate_employee_id(self, value):
        # Skip validation during update if employee_id isn't provided
        if self.instance is not None and not value:
            return None
            
        try:
            return Employee.objects.get(employee_id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee with this ID does not exist.")
    
    def validate(self, data):
        """
        Validate the entire data set for leave request creation or update
        """
        # For updates, modify validation to only check provided fields
        if self.instance is not None:
            # Get start_date and end_date, falling back to instance values if not provided
            start_date = data.get('start_date', self.instance.start_date)
            end_date = data.get('end_date', self.instance.end_date)
            
            # Only validate dates if both are provided or if either was changed
            if (start_date != self.instance.start_date or end_date != self.instance.end_date) and start_date and end_date:
                if end_date < start_date:
                    raise serializers.ValidationError({"end_date": "End date must be after start date."})
            
            return data
            
        # For create operations, do full validation
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            # Ensure end date is after start date
            if end_date < start_date:
                raise serializers.ValidationError({"end_date": "End date must be after start date."})
            
            # Check for past dates only on create
            today = timezone.now().date()
            if start_date < today:
                raise serializers.ValidationError({"start_date": "Leave request start date cannot be in the past."})
        
        # Validate leave type
        if not data.get('leave_type'):
            raise serializers.ValidationError({"leave_type": "Leave type is required."})
        
        # Check for overlapping leave requests on create
        employee = data.get('employee_id')
        if employee and start_date and end_date:
            if Employee_Leave_Request.objects.filter(
                employee=employee,
                status="Pending",
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exists():
                raise serializers.ValidationError({
                    "non_field_errors": "An active leave request already exists for these dates."
                })
        
        return data

    def create(self, validated_data):
        employee = validated_data.pop('employee_id')
        
        # Get employee's department and set it automatically
        dept = employee.dept
        if not dept:
            raise serializers.ValidationError({"employee_id": "Selected employee has no department assigned."})
        
        # Calculate total_days
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        
        total_days = None
        if start_date and end_date:
            delta = end_date - start_date
            total_days = delta.days + 1  # Including both start and end days
        
        # Extract and process immediate_superior_id if it exists
        immediate_superior_id = validated_data.pop('immediate_superior_id', None)
        
        # Extract and process management_approval_id if it exists
        management_approval_id = validated_data.pop('management_approval_id', None)
        
        # Create the leave request with all required fields
        try:
            return Employee_Leave_Request.objects.create(
                employee=employee,
                dept=dept,
                total_days=total_days,
                immediate_superior_id=immediate_superior_id,
                management_approval_id=management_approval_id,
                **validated_data
            )
        except Exception as e:
            # Catch any unexpected errors during creation
            raise serializers.ValidationError(f"Failed to create leave request: {str(e)}")

    def update(self, instance, validated_data):
        # Handle employee_id only if it's explicitly provided
        if 'employee_id' in validated_data:
            employee = validated_data.pop('employee_id')
            if employee:  # Only update if there's a valid employee
                instance.employee = employee
                # Update dept if employee changed
                instance.dept = employee.dept
            
        # Handle immediate_superior_id
        immediate_superior_id = validated_data.pop('immediate_superior_id', None)
        if immediate_superior_id is not None:  # Only set if explicitly provided
            instance.immediate_superior_id = immediate_superior_id
            
        # Handle management_approval_id
        management_approval_id = validated_data.pop('management_approval_id', None)
        if management_approval_id is not None:  # Only set if explicitly provided
            instance.management_approval_id = management_approval_id
            
        # Recalculate total_days if start_date or end_date changed
        start_date = validated_data.get('start_date', instance.start_date)
        end_date = validated_data.get('end_date', instance.end_date)
        
        if start_date and end_date:
            delta = end_date - start_date
            instance.total_days = delta.days + 1
            
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance