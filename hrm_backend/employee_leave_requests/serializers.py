from rest_framework import serializers
from .models import Employee_Leave_Request
from employees.models import Employee
from django.utils import timezone
from datetime import datetime

class Employee_Leave_Request_Serializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.SerializerMethodField()
    immediate_superior_name = serializers.SerializerMethodField()
    # management_approval_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee_Leave_Request
        fields = [
            'leave_id',
            'employee_id',
            'employee_name',
            'dept_id',
            'immediate_superior_id',
            'immediate_superior_name',
            # 'management_approval_id',
            # 'management_approval_name',
            'leave_type',
            'start_date',
            'end_date',
            'total_days',
            'is_paid',
            'reason',
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
                superior = Employee.objects.get(employee_id = obj.immediate_superior_id)
                return f"{superior.first_name} {superior.last_name}"
            except Employee.DoesNotExist:
                return "N/A"
        return "N/A"

    # def get_management_approval_name(self, obj):
    #     if obj.management_approval_id:
    #         try:
    #             management_approval = Employee.objects.get(employee_id = obj.management_approval_id)
    #             return f"{management_approval.first_name} {management_approval.last_name}"
    #         except Employee.DoesNotExist:
    #             return "N/A"
    #     return "N/A"

class Employee_Leave_Request_CreateSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(write_only = True, required = False)
    immediate_superior_id = serializers.CharField(required = False, allow_null = True, allow_blank = True, write_only = True)
    management_approval_id = serializers.CharField(required = False, allow_null = True, allow_blank = True, write_only = True)

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
            'reason',
            'status',
        ]

    def validate_employee_id(self, value):
        if self.instance is not None and not value:
            return None
            
        try:
            return Employee.objects.get(employee_id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee with this ID does not exist.")
    
    def validate(self, data):
        if self.instance is not None:
            start_date = data.get('start_date', self.instance.start_date)
            end_date = data.get('end_date', self.instance.end_date)
            
            if (start_date != self.instance.start_date or end_date != self.instance.end_date) and start_date and end_date:
                if end_date < start_date:
                    raise serializers.ValidationError({"end_date": "End date must be after start date."})
            
            return data
            
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({"end_date": "End date must be after start date."})
            
            today = timezone.now().date()
            if start_date < today:
                raise serializers.ValidationError({"start_date": "Leave request start date cannot be in the past."})
        
        if not data.get('leave_type'):
            raise serializers.ValidationError({"leave_type": "Leave type is required."})
        
        employee = data.get('employee_id')
        if employee and start_date and end_date:
            if Employee_Leave_Request.objects.filter(
                employee = employee,
                status = "Pending",
                start_date__lte = end_date,
                end_date__gte = start_date
            ).exists():
                raise serializers.ValidationError({
                    "non_field_errors": "An active leave request already exists for these dates."
                })
        
        return data

    def create(self, validated_data):
        employee = validated_data.pop('employee_id')
        
        dept = employee.dept
        if not dept:
            raise serializers.ValidationError({"employee_id": "Selected employee has no department assigned."})
        
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        
        total_days = None
        if start_date and end_date:
            delta = end_date - start_date
            total_days = delta.days + 1
        
        immediate_superior_id = validated_data.pop('immediate_superior_id', None)
        management_approval_id = validated_data.pop('management_approval_id', None)
        
        try:
            return Employee_Leave_Request.objects.create(
                employee = employee,
                dept = dept,
                total_days = total_days,
                immediate_superior_id = immediate_superior_id,
                management_approval_id = management_approval_id,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create leave request: {str(e)}")

    def update(self, instance, validated_data):
        if 'employee_id' in validated_data:
            employee = validated_data.pop('employee_id')
            if employee:
                instance.employee = employee
                instance.dept = employee.dept
            
        immediate_superior_id = validated_data.pop('immediate_superior_id', None)
        if immediate_superior_id is not None:
            instance.immediate_superior_id = immediate_superior_id
            
        management_approval_id = validated_data.pop('management_approval_id', None)
        if management_approval_id is not None: 
            instance.management_approval_id = management_approval_id
            
        start_date = validated_data.get('start_date', instance.start_date)
        end_date = validated_data.get('end_date', instance.end_date)
        
        if start_date and end_date:
            delta = end_date - start_date
            instance.total_days = delta.days + 1
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance