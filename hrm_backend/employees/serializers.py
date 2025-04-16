from rest_framework import serializers
from .models import Employee, Department, Position
from rest_framework.exceptions import ValidationError

class Employee_Serializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(read_only = True)
    user_id = serializers.CharField(write_only = True)
    dept_name = serializers.CharField(write_only = True, required = False)
    dept_id = serializers.CharField(write_only = True)
    position_name = serializers.CharField(write_only = True)
    position_id = serializers.CharField(write_only = True)
    first_name = serializers.CharField(max_length = 255)
    last_name = serializers.CharField(max_length = 255)
    status = serializers.ChoiceField(choices = Employee.STATUS_CHOICES)
    reports_to = serializers.CharField(max_length = 255, required = False, allow_null = True)
    salary_grade = serializers.CharField(read_only = True)
    phone = serializers.CharField(max_length = 15, required = False)
    is_supervisor = serializers.BooleanField()

    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'user_id',
            'dept_id',
            'dept_name',
            'position_id',
            'position_name',
            'first_name',
            'last_name',
            # 'email',
            'phone',
            'employment_type',
            'status',
            'reports_to',
            'salary_grade',
            'is_supervisor',
            'created_at',
            'updated_at',
            'is_archived',
        ]
        read_only_fields = ['employee_id']
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep = {
            'employee_id': instance.employee_id,
            'user_id': instance.user_id,
            'dept_id': instance.dept.dept_id if instance.dept else None,
            'dept_name': instance.dept.dept_name if instance.dept else None,
            'position_id': instance.position.position_id if instance.position else None,
            'position_title': instance.position.position_title if instance.position else None,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'phone': instance.phone,
            'status': instance.status,
            'is_supervisor': instance.is_supervisor,
            'reports_to': instance.reports_to,
            'salary_grade': instance.position.salary_grade if instance.position else None,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'is_archived': instance.is_archived,
        }

        if self.context['request'].method in ['PUT', 'PATCH']:
            rep = {
                'dept_name': instance.dept.dept_name if instance.dept else None,
                'position_title': instance.position.position_title if instance.position else None,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'phone': instance.phone,
                'status': instance.status,
                'is_supervisor': instance.is_supervisor,
                'reports_to': instance.reports_to,
                'is_archived': instance.is_archived,
            }

        return rep

    def create(self, validated_data):
        dept_name = validated_data.pop('dept_name', None)
        position_name = validated_data.pop('position_name', None)
        reports_to = validated_data.pop('reports_to', None)

        if dept_name:
            try:
                department = Department.objects.get(dept_name=dept_name)
                validated_data['dept'] = department
            except Department.DoesNotExist:
                raise ValidationError(f"Department '{dept_name}' does not exist.")

        if position_name:
            position = Position.objects.get(position_title=position_name)
            validated_data['position'] = position
        
        if reports_to:
            try:
                first_name, last_name = reports_to.split(' ', 1)  # Split by space
                reports_to_employee = Employee.objects.get(first_name=first_name, last_name=last_name)
                validated_data['reports_to'] = reports_to_employee
            except Employee.DoesNotExist:
                raise ValidationError(f"Employee '{reports_to}' does not exist.")
            except ValueError:
                raise ValidationError("Invalid employee name format. Use 'First Last'.")

        employee = Employee.objects.create(**validated_data)
        return employee

    def update(self, instance, validated_data):
        dept_name = validated_data.pop('dept_name', None)
        position_name = validated_data.pop('position_name', None)
        reports_to = validated_data.pop('reports_to', None)

        if dept_name:
            try:
                department = Department.objects.get(dept_name=dept_name)
                validated_data['dept'] = department
            except Department.DoesNotExist:
                raise ValidationError(f"Department '{dept_name}' does not exist.")
        
        if position_name:
            position = Position.objects.get(position_title = position_name)
            validated_data['position'] = position
        
        if reports_to:
            try:
                first_name, last_name = reports_to.split(' ', 1)
                reports_to_employee = Employee.objects.get(first_name = first_name, last_name = last_name)
                validated_data['reports_to'] = reports_to_employee
            except Employee.DoesNotExist:
                raise ValidationError(f"Employee '{reports_to}' does not exist.")
            except ValueError:
                raise ValidationError("Invalid employee name format. Use 'First Last'.")

        return super().update(instance, validated_data)

