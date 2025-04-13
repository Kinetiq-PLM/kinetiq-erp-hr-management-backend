from django import forms
from .models import Department_Superior
from employees.models import Employee

class Department_Superior_Admin_Form(forms.ModelForm):
    class Meta:
        model = Department_Superior
        fields = ['employee', 'hierarchy_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = self.instance
        if instance and instance.pk:
            dept = instance.dept
            position = instance.position

            if dept and position:
                self.fields['employee'].queryset = Employee.objects.filter(
                    dept=dept,
                    position=position,
                    is_archived=False,
                    status='Active'
                )
            else:
                self.fields['employee'].queryset = Employee.objects.none()
        else:
            self.fields['employee'].queryset = Employee.objects.none()
