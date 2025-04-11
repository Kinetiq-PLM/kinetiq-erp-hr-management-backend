# run this if you want recompute the employee performance records (i already did so nothing works if you re run it)
# 1st created command
# python manage.py recompute_bonus

from django.core.management.base import BaseCommand
from employee_performance.models import EmployeePerformance


class Command(BaseCommand):
    help = 'Recomputes bonus_amount for all EmployeePerformance records.'

    def handle(self, *args, **kwargs):
        performances = EmployeePerformance.objects.all()
        total = performances.count()
        updated = 0

        if not total:
            self.stdout.write(self.style.WARNING('No EmployeePerformance records found.'))
            return

        self.stdout.write(f'Found {total} records. Recomputing bonus_amount...')

        for perf in performances:
            old_bonus = perf.bonus_amount
            perf.bonus_amount = perf.calculate_bonus_amount()
            perf.save()
            updated += 1
            self.stdout.write(
                f'Updated {perf.performance_id} | Old: {old_bonus} -> New: {perf.bonus_amount}'
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} records!'))
