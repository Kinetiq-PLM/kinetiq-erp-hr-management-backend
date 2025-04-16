from rest_framework import serializers
from .models import Payroll

class Payroll_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = [
            'payroll_id', 'gross_pay', 'total_deductions',
            'net_pay', 'created_at', 'updated_at'
        ]

class Payroll_CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = [
            'employee_id',
            'pay_period_start',
            'pay_period_end',
        ]

class Payroll_UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = [
            'status',
        ]

    def create(self, validated_data):
        payroll = super().create(validated_data)
        payroll.save()
        return payroll

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.save()
        return instance