from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

class Payroll(models.Model):
    # xample na constant
    SSS_RATE = 0.11
    PHILHEALTH_RATE = 0.04 
    PAGIBIG_RATE = 0.02 
    TAX_RATE = 0.10 

    STATUS_CHOICES = [
            ('Draft', 'Draft'),
            ('Finalized', 'Finalized'),
            ('Locked', 'Locked')
        ]

    payroll_id = models.CharField(primary_key = True, max_length = 255, default = uuid.uuid4, editable = False)
    employee_id = models.CharField(max_length = 255)
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    employment_type = models.CharField(max_length = 20)

    base_salary = models.DecimalField(max_digits = 12, decimal_places = 2)
    overtime_hours = models.DecimalField(max_digits = 5, decimal_places = 2, default = 0)
    overtime_pay = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    holiday_pay = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    bonus_pay = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    thirteenth_month_pay = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    gross_pay = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    sss_contribution = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    philhealth_contribution = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    pagibig_contribution = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    tax = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    late_deduction = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    absent_deduction = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    undertime_deduction = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    total_deductions = models.DecimalField(max_digits = 12, decimal_places = 2, default=0)
    net_pay = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default = 'Draft')
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'payroll'
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payroll'

    def finalize_payroll(self):
        if self.status == 'Draft':
            self.status = 'Finalized'
            self.save()
        else:
            raise ValueError("Payroll cannot be finalized after it has been finalized or locked.")

    def lock_payroll(self):
        if self.status == 'Finalized':
            self.status = 'Locked'
            self.save()
        else:
            raise ValueError("Payroll must be finalized before it can be locked.")

    def reset_payroll(self):
        if self.status == 'Draft':
            self.status = 'Draft'
            self.save()
        else:
            raise ValueError("Payroll can only be reset if it's in Draft status.")
        
    def calculate_sss_contribution(self):
        self.sss_contribution = self.base_salary * self.SSS_RATE
        return self.sss_contribution

    def calculate_philhealth_contribution(self):
        self.philhealth_contribution = self.base_salary * self.PHILHEALTH_RATE
        return self.philhealth_contribution

    def calculate_pagibig_contribution(self):
        self.pagibig_contribution = self.base_salary * self.PAGIBIG_RATE
        return self.pagibig_contribution
    
    def calculate_tax(self):
        self.tax = self.gross_pay * self.TAX_RATE
        return self.tax
    
    def clean(self):
        if self.status == 'Finalized' and self.pk and self.status != 'Draft':
            previous_instance = Payroll.objects.get(pk=self.pk)
            if previous_instance.status == 'Finalized' and self.status == 'Draft':
                raise ValidationError("Cannot revert payroll status from Finalized to Draft.")
        
        if self.status == 'Locked' and self.pk:
            previous_instance = Payroll.objects.get(pk=self.pk)
            if previous_instance.status == 'Locked':
                raise ValidationError("Payroll is already locked and cannot be edited.")

    def save(self, *args, **kwargs):
        # recalculate the contribtuons when saving the payroll
        self.sss_contribution = self.calculate_sss_contribution()
        self.philhealth_contribution = self.calculate_philhealth_contribution()
        self.pagibig_contribution = self.calculate_pagibig_contribution()
        self.tax = self.calculate_tax() # tax calcualation

        # recalcualte the deudctuon and net pay
        self.gross_pay = self.base_salary + self.overtime_pay + self.holiday_pay + self.bonus_pay + self.thirteenth_month_pay
        self.total_deductions = self.sss_contribution + self.philhealth_contribution + self.pagibig_contribution + self.tax + self.late_deduction + self.absent_deduction + self.undertime_deduction
        self.net_pay = self.gross_pay - self.total_deductions

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payroll_id} | {self.employee_id} | {self.status}"