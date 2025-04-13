from rest_framework import serializers
from .models import Department_Superior, Position, Department

class Department_Superior_Serializer(serializers.ModelSerializer):
    dept_superior_id = serializers.CharField()
    dept_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    superior_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Department_Superior
        fields = [
            'dept_superior_id',
            'dept_id',
            'dept_name',
            'position_title',
            'position_id',
            'employee_id',
            'superior_name',
            'phone',
            'status',
            'hierarchy_level',
            'is_archived'
        ]

    def get_dept_name(self, obj):
        return obj.dept.dept_name if obj.dept else None

    def get_position_title(self, obj):
        return obj.position.position_title if obj.position else None

    def get_employee_id(self, obj):
        return obj.employee.id if obj.employee else None

    def get_superior_name(self, obj):
        emp = obj.employee
        return f"{emp.first_name} {emp.last_name}" if emp else None

    def get_phone(self, obj):
        emp = obj.employee
        return emp.phone if emp else None

    def get_status(self, obj):
        emp = obj.employee
        return emp.status if emp else None

class Department_Superior_WriteSerializer(serializers.ModelSerializer):
    dept_name = serializers.CharField(write_only = True, required = True)
    position_title = serializers.CharField(write_only = True, required = True)

    class Meta:
        model = Department_Superior
        fields = ['dept_name', 'position_title', 'hierarchy_level', 'is_archived']

    def create(self, validated_data):
        dept_name = validated_data.pop('dept_name')
        position_title = validated_data.pop('position_title')

        dept, _ = Department.objects.get_or_create(dept_name = dept_name)
        position, _ = Position.objects.get_or_create(position_title = position_title)

        dept_superior = Department_Superior.objects.create(
            dept = dept,
            position = position,
            **validated_data
        )

        return dept_superior

    def update(self, instance, validated_data):
        dept_name = validated_data.pop('dept_name', None)
        position_title = validated_data.pop('position_title', None)

        if dept_name:
            dept, _ = Department.objects.get_or_create(dept_name = dept_name)
            instance.dept = dept

        if position_title:
            position, _ = Position.objects.get_or_create(position_title = position_title)
            instance.position = position

        instance.hierarchy_level = validated_data.get('hierarchy_level', instance.hierarchy_level)
        instance.is_archived = validated_data.get('is_archived', instance.is_archived)

        instance.save()
        return instance

class Department_Superior_History_Serializer(serializers.ModelSerializer):
    history_user = serializers.CharField(source="history_user.username", read_only = True)
    history_change_reason = serializers.CharField(read_only = True)
    history_date = serializers.DateTimeField(read_only = True)
    status = serializers.SerializerMethodField()
    dept_name = serializers.CharField(source='dept.dept_name', read_only = True)

    class Meta:
        model = Department.history.model
        fields = ['history_user', 'history_change_reason', 'history_date', 'status', 'dept_name']

    def get_status(self, obj):
        if obj.history_change_reason:
            return "Changed"
        else:
            return "Unchanged"
