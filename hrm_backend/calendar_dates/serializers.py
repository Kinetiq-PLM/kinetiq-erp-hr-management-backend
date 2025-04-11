from rest_framework import serializers
from .models import Calendar_Date

class Calendar_Date_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar_Date
        fields = ['date', 'is_workday', 'is_holiday', 'is_special', 'holiday_name']
