from django.core.management.base import BaseCommand
from simple_history.utils import update_change_reason
from positions.models import Position

class Command(BaseCommand):
    help = 'Clear historical records for Position model'

    def handle(self, *args, **kwargs):
        Historical_Position = Position.history.model
        Historical_Position.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared history for Position model.'))
