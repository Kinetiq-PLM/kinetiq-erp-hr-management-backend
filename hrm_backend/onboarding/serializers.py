from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Onboarding

class Onboarding_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Onboarding
        fields = [
            'onboarding_id',
            'candidate',
            'job',
            'offer_details',
            'contract_details',
            'status',
            'created_at',
            'updated_at',
            'is_archived'
        ]

    def validate_onboarding_id(self, value):
        if Onboarding.objects.filter(onboarding_id = value).exists():
            raise ValidationError(f"Onboarding ID '{value}' already exists.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep = {
            'onboarding_id': rep.get('onboarding_id'),
            'candidate': rep.get('candidate'),
            'job': rep.get('job'),
            'offer_details': rep.get('offer_details'),
            'contract_details': rep.get('contract_details'),
            'status': rep.get('status'),
            'created_at': rep.get('created_at'),
            'updated_at': rep.get('updated_at'),
            'is_archived': rep.get('is_archived'),
        }
        return rep
