from django.db import models
from employees.models import Employee

class EmployeePerformance(models.Model):
    performance_id = models.CharField(max_length=255, primary_key=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column='employee_id',
        related_name='performance_reviews'
    )
    immediate_superior = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='immediate_superior_id',
        related_name='supervised_performances'
    )
    rating = models.IntegerField(choices=[
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])

    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    review_date = models.DateField(auto_now_add=False)
    comments = models.TextField(null=True, blank=True)
    bonus_payment_month = models.IntegerField(
        choices=MONTH_CHOICES,
        null=True,
        blank=True,
        help_text="Month when bonus will be paid."
    )

    class Meta:
        db_table = 'employee_performance'

    def __str__(self):
        return f'{self.performance_id} - {self.employee_id}'
