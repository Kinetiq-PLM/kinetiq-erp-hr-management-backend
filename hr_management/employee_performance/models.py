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
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    review_date = models.DateField(auto_now_add=False)
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=False)
    updated_at = models.DateTimeField(auto_now=False)

    class Meta:
        db_table = 'employee_performance'

    def __str__(self):
        return f'{self.performance_id} - {self.employee_id}'
