from rest_framework import serializers
from .models import Department_Superior, Position, Department
from employees.models import Employee
from rest_framework.exceptions import ValidationError

class Department_Superior_Serializer(serializers.ModelSerializer):
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
            'position_id',
            'position_title',
            'employee_id',
            'superior_name',
            'phone',
            'status',
            'hierarchy_level',
            'is_archived',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if self.context['request'].method in ['PUT', 'PATCH']:
            rep.pop('dept_superior_id', None)
            rep.pop('employee_id', None)
            rep.pop('superior_name', None)
            rep.pop('phone', None)
            rep.pop('status', None)

        return rep

    def create(self, validated_data):
        dept = validated_data.get('dept')
        position = validated_data.get('position')

        if not Employee.objects.filter(dept = dept, position = position, is_archived = False).exists():
            raise ValidationError(f"No active employee found for department '{dept.dept_name}' and position '{position.position_title}'.")

        return Department_Superior.objects.create(**validated_data)

    def get_dept_name(self, obj):
        return obj.dept.dept_name if obj.dept else None

    def get_position_title(self, obj):
        return obj.position.position_title if obj.position else None

    def get_employee_id(self, obj):
        emp = obj.get_employee()
        return emp.employee_id if emp else None

    def get_superior_name(self, obj):
        emp = obj.get_employee()
        if emp:
            first_name = emp.first_name
            last_name = emp.last_name
            return f"{first_name} {last_name}" if first_name and last_name else None
        return None

    def get_phone(self, obj):
        emp = obj.get_employee()
        return emp.phone if emp else None

    def get_status(self, obj):
        emp = obj.get_employee()
        return emp.status if emp else None

class Department_Superior_CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department_Superior
        fields = ['hierarchy_level']
