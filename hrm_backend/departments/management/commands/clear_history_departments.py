from django.core.management.base import BaseCommand
from simple_history.utils import update_change_reason
from department_superiors.models import Department_Superior

class Command(BaseCommand):
    help = 'Clear historical records for Department Superior model'

    def handle(self, *args, **kwargs):
        Historical_Department_Superior = Department_Superior.history.model
        Historical_Department_Superior.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared history for Department Superior model.'))
