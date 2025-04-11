from django.core.management.base import BaseCommand
from simple_history.utils import update_change_reason
from departments.models import Department

class Command(BaseCommand):
    help = 'Clear historical records for Department model'

    def handle(self, *args, **kwargs):
        # Get the related historical model for the Department model
        HistoricalDepartment = Department.history.model
        
        # Delete all historical records for the Department model
        HistoricalDepartment.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared history for Department model.'))
