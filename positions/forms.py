from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Position

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        employment_type = self.initial.get('employment_type', self.instance.employment_type)

        if employment_type == 'Regular':
            self.fields['typical_duration_days'].disabled = True
            self.fields['typical_duration_days'].help_text = 'No duration needed for Regular positions.'

        elif employment_type == 'Contractual':
            self.fields['typical_duration_days'].initial = 30
            self.fields['typical_duration_days'].help_text = 'Must be between 30 and 180 days.'

        elif employment_type == 'Seasonal':
            self.fields['typical_duration_days'].initial = 1
            self.fields['typical_duration_days'].help_text = 'Must be between 1 and 29 days.'
