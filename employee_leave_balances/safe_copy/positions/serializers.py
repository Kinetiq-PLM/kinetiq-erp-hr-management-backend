from rest_framework import serializers
from .models import Position

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'
        read_only_fields = ('position_id', 'created_at', 'updated_at')
