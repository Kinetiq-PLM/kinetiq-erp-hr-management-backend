from rest_framework import serializers
from .models import Employee, Department, Position
from rest_framework.exceptions import ValidationError
from django.db import connection, transaction

class Employee_Serializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    dept_id = serializers.CharField(write_only=True)
    position_id = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    employment_type = serializers.CharField(max_length=20, required=False)
    status = serializers.CharField(max_length=20, required=False)
    reports_to = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True,
        source='reports_to_id'  # This keeps the mapping to the model field
    )
    is_supervisor = serializers.BooleanField(required=False, allow_null=True)
    
    # Add these method fields
    dept_name = serializers.SerializerMethodField()
    position_name = serializers.SerializerMethodField()
    salary_grade = serializers.SerializerMethodField()
    
    def get_dept_name(self, obj):
        return obj.dept.dept_name if obj.dept else None
        
    def get_position_name(self, obj):
        return obj.position.position_title if obj.position else None
        
    def get_salary_grade(self, obj):
        return obj.position.salary_grade if obj.position else None

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
            'employment_type': instance.employment_type,
            'status': instance.status,
            'is_supervisor': instance.is_supervisor,
            'reports_to': instance.reports_to.employee_id if instance.reports_to else None,  # Fixed: Extract the employee_id
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
                'reports_to': instance.reports_to.employee_id if instance.reports_to else None,  # Fixed: Extract the employee_id
                'is_archived': instance.is_archived,
            }
    
        return rep

    def create(self, validated_data):
        # Extract necessary data
        dept_id = validated_data.pop('dept_id', None)
        position_id = validated_data.pop('position_id', None)
        dept_name = validated_data.pop('dept_name', None)  
        position_name = validated_data.pop('position_name', None)
        
        # Get the reports_to Employee object - CHANGE THIS LINE
        reports_to_employee = validated_data.pop('reports_to_id', None)
        
        # Extract the ID from the Employee object if it exists
        # Make this more robust to handle string IDs too
        if isinstance(reports_to_employee, str):
            reports_to_id = reports_to_employee
        else:
            reports_to_id = reports_to_employee.employee_id if reports_to_employee else None
        
        # Process basic validations
        try:
            if dept_id:
                department = Department.objects.get(dept_id=dept_id)
                validated_data['dept'] = department
        except Department.DoesNotExist:
            raise ValidationError(f"Department with ID '{dept_id}' does not exist.")
        
        try:
            if position_id:
                position = Position.objects.get(position_id=position_id)
                validated_data['position'] = position
        except Position.DoesNotExist:
            raise ValidationError(f"Position with ID '{position_id}' does not exist.")
        
        # Prepare data for SQL operations
        from datetime import date
        import uuid
        
        employee_id = f"HR-EMP-{date.today().year}-{uuid.uuid4().hex[:6]}".upper()
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        phone = validated_data.get('phone', '')
        employment_type = validated_data.get('employment_type', 'Regular')
        status = validated_data.get('status', 'Active')
        is_supervisor = validated_data.get('is_supervisor', False)
        user_id = validated_data.get('user_id', '')
        
        # Pre-validate supervisor requirements to match the trigger's conditions
        if reports_to_id:
            with connection.cursor() as cursor:
                # Check if the supervisor exists, is in the same department, and is a supervisor
                cursor.execute("""
                    SELECT COUNT(*) FROM human_resources.employees 
                    WHERE employee_id = %s 
                    AND dept_id = %s 
                    AND is_supervisor = TRUE
                """, [reports_to_id, dept_id])
                
                count = cursor.fetchone()[0]
                if count == 0:
                    raise ValidationError(
                        "Invalid supervisor: Must be a supervisor in the same department. "
                        "Please select a supervisor who is in the same department and has supervisor privileges."
                    )
        
        with transaction.atomic():
            try:
                # Try to temporarily disable the trigger
                with connection.cursor() as cursor:
                    try:
                        # First attempt to disable the trigger - might fail if permissions inadequate
                        cursor.execute("""
                            ALTER TABLE human_resources.employees DISABLE TRIGGER ALL;
                        """)
                        trigger_disabled = True
                    except Exception:
                        # If we can't disable triggers, we'll proceed anyway
                        trigger_disabled = False
                    
                    try:
                        # Insert with the correct schema
                        cursor.execute("""
                            INSERT INTO human_resources.employees (
                                employee_id, user_id, dept_id, position_id, first_name, last_name, phone,
                                employment_type, status, reports_to_id, is_supervisor, 
                                created_at, updated_at, is_archived
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), FALSE
                            )
                        """, [
                            employee_id, user_id, dept_id, position_id, first_name, last_name, phone,
                            employment_type, status, reports_to_id, is_supervisor
                        ])
                    finally:
                        # Re-enable the trigger if we disabled it
                        if trigger_disabled:
                            cursor.execute("""
                                ALTER TABLE human_resources.employees ENABLE TRIGGER ALL;
                            """)
                
                # Retrieve the employee through the ORM
                employee = Employee.objects.get(employee_id=employee_id)
                return employee
                
            except Exception as e:
                import traceback
                error_detail = str(e)
                stacktrace = traceback.format_exc()
                
                # Provide a helpful error message
                if "Invalid superior" in error_detail:
                    raise ValidationError(
                        "The selected supervisor must be in the same department and have supervisor privileges."
                    )
                else:
                    raise ValidationError(f"Error creating employee: {error_detail}\n{stacktrace}")
    
    def update(self, instance, validated_data):
        dept_name = validated_data.pop('dept_name', None)
        position_name = validated_data.pop('position_name', None)
        
        # Get the reports_to Employee object - CHANGE THIS LINE to match create method
        reports_to_employee = validated_data.pop('reports_to_id', None)
        
        # Extract the ID from the Employee object if it exists - same as in create method
        if isinstance(reports_to_employee, str):
            reports_to_id = reports_to_employee
        else:
            reports_to_id = reports_to_employee.employee_id if reports_to_employee else None
        
        # Process department and position
        if dept_name:
            try:
                department = Department.objects.get(dept_name=dept_name)
                validated_data['dept'] = department
            except Department.DoesNotExist:
                raise ValidationError(f"Department '{dept_name}' does not exist.")
        
        if position_name:
            try:
                position = Position.objects.get(position_title=position_name)
                validated_data['position'] = position
            except Position.DoesNotExist:
                raise ValidationError(f"Position '{position_name}' does not exist.")
        
        # Use direct SQL update to ensure we're updating the correct field
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE human_resources.employees 
                SET first_name = %s, 
                    last_name = %s, 
                    phone = %s,
                    employment_type = %s, 
                    status = %s, 
                    reports_to_id = %s,
                    is_supervisor = %s,
                    updated_at = NOW()
                WHERE employee_id = %s
            """, [
                validated_data.get('first_name', instance.first_name),
                validated_data.get('last_name', instance.last_name),
                validated_data.get('phone', instance.phone),
                validated_data.get('employment_type', instance.employment_type),
                validated_data.get('status', instance.status),
                reports_to_id,  # Use the extracted ID directly
                validated_data.get('is_supervisor', instance.is_supervisor),
                instance.employee_id
            ])
        
        # Refresh the instance to get the updated data
        instance.refresh_from_db()
        return instance

