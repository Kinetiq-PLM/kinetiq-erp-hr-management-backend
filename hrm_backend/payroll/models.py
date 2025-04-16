from django.db import models
from django.utils import timezone
from employee_leave_requests.models import Employee_Leave_Request
from attendance_tracking.models import Attendance_Tracking
from calendar_dates.models import Calendar_Date
from employee_performance.models import Employee_Performance
# from employee_salary.models import Employee_Salary
# from employees.models import Employee
from django.core.exceptions import ValidationError
import uuid
from datetime import timedelta

class Payroll(models.Model):
    # xample na constant
    SSS_RATE = 0.11
    PHILHEALTH_RATE = 0.04 
    PAGIBIG_RATE = 0.02 
    TAX_RATE = 0.10 
    OVERTIME_RATE = 1.5

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
    
    def update_leave_balance_after_payroll(self):
        leave_requests = Employee_Leave_Request.objects.filter(
            employee=self.employee_id,
            status="Approved",
            start_date__gte=self.pay_period_start,
            end_date__lte=self.pay_period_end
        )

        leave_balance = self.employee.leave_balance
        for leave in leave_requests:
            if leave.is_paid:
                leave_balance.sick_leave += leave.total_days
            else:
                leave_balance.sick_leave -= leave.total_days

        leave_balance.save()
    
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
        attendances = Attendance_Tracking.objects.filter(
            employee_id = self.employee_id,
            date__range = (self.pay_period_start, self.pay_period_end)
        )

        self.late_deduction = sum(a.late_hours for a in attendances) * (self.base_salary / 30 / 8)
        self.absent_deduction = sum(1 for a in attendances if a.status == 'Absent') * (self.base_salary / 30)
        self.undertime_deduction = sum(a.undertime_hours for a in attendances) * (self.base_salary / 30 / 8)

        self.overtime_hours = sum(a.overtime_hours for a in attendances)
        self.overtime_pay = self.overtime_hours * (self.base_salary / 30 / 8) * self.OVERTIME_RATE

        # holiday pay
        holidays = Calendar_Date.objects.filter(
            date__range = (self.pay_period_start, self.pay_period_end),
            is_holiday = True
        )
        self.holiday_pay = 0
        for holiday in holidays:
            att = attendances.filter(date = holiday.date).first()
            if att and att.status == 'Present':
                self.holiday_pay += (self.base_salary / 30) * 2 if holiday.holiday_type == 'Regular' else (self.base_salary / 30) * 1.3

        # bonus
        perf = Employee_Performance.objects.filter(
            employee_id = self.employee_id,
            review_date__range = (self.pay_period_start, self.pay_period_end)
        ).first()
        self.bonus_pay = perf.bonus_amount if perf else 0

        # 13th month
        if self.pay_period_end.month == 12 and self.employment_type == 'Regular':
            self.thirteenth_month_pay = self.base_salary / 2

        # the base gross pay before leave adjustment
        self.gross_pay = self.base_salary + self.overtime_pay + self.holiday_pay + self.bonus_pay + self.thirteenth_month_pay

        # add the leave pay
        leave_requests = Employee_Leave_Request.objects.filter(
            employee = self.employee_id,
            status = "Approved",
            start_date__lte = self.pay_period_end,
            end_date__gte = self.pay_period_start
        )

        for leave in leave_requests:
            if leave.is_paid:
                paid_leave_pay = leave.total_days * (self.base_salary / 30)
                self.gross_pay += paid_leave_pay

        # recalculate contributions after updated gross
        self.sss_contribution = self.calculate_sss_contribution()
        self.philhealth_contribution = self.calculate_philhealth_contribution()
        self.pagibig_contribution = self.calculate_pagibig_contribution()

        # recalculate tax after gross is finalized
        self.tax = self.calculate_tax()

        # unpaid leave deductions
        total_leave_deductions = sum(
            leave.total_days * (self.base_salary / 30)
            for leave in leave_requests
            if not leave.is_paid
        )

        # comptue the total deductions and net pay
        self.total_deductions = (
            self.sss_contribution +
            self.philhealth_contribution +
            self.pagibig_contribution +
            self.tax +
            self.late_deduction +
            self.absent_deduction +
            self.undertime_deduction +
            total_leave_deductions
        )
        self.net_pay = self.gross_pay - self.total_deductions

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payroll_id} | {self.employee_id} | {self.status}"
