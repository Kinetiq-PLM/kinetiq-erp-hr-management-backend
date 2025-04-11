from django.core.management.base import BaseCommand
from simple_history.utils import update_change_reason
from employees.models import Employee

class Command(BaseCommand):
    help = 'Clear historical records for Department Superior model'

    def handle(self, *args, **kwargs):
        # Get the related historical model for the Department model
        Historical_Employees = Employee.history.model
        
        # Delete all historical records for the Department model
        Historical_Employees.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared history for Employee model.'))
