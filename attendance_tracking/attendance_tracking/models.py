from django.db import models
from employees.models import Employee
from calendar_dates.models import Calendar_Date
from django.utils import timezone

class Attendance_Tracking(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Clocked Out', 'Clocked Out'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
    ]

    def get_default_employee():
        try:
            return Employee.objects.get(employee_id="HR-EMP-0000").id
        except Employee.DoesNotExist:
            return None

    attendance_id = models.CharField(max_length=20, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances", default=get_default_employee)
    date = models.DateField()
    time_in = models.DateTimeField()
    time_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Present")
    late_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    undertime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_holiday = models.BooleanField(default=False)
    holiday_type = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    calendar_date = models.ForeignKey(Calendar_Date, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if holiday or special day
        calendar_date = Calendar_Date.objects.filter(date=self.date).first()
        if calendar_date:
            self.is_holiday = calendar_date.is_holiday
            self.holiday_type = 'Holiday' if calendar_date.is_holiday else ('Special' if calendar_date.is_special else '')

        # Ensure time_in is timezone-aware
        if timezone.is_naive(self.time_in):
            self.time_in = timezone.make_aware(self.time_in, timezone.get_current_timezone())

        # Compute late hours
        standard_start_time = timezone.make_aware(
            timezone.datetime(self.date.year, self.date.month, self.date.day, 9, 0),
            timezone.get_current_timezone()
        )

        if self.time_in > standard_start_time:
            self.late_hours = round((self.time_in - standard_start_time).total_seconds() / 3600, 2)
        else:
            self.late_hours = 0

        # Compute work hours if time_out exists
        if self.time_in and self.time_out:
            # Allow time_out to be on the next day
            worked_seconds = (self.time_out - self.time_in).total_seconds()

            if worked_seconds < 0:
                raise ValueError("Time Out cannot be earlier than Time In.")

            worked = worked_seconds / 3600  # Convert to hours
            expected_hours = 8

            # Always reset values first
            self.undertime_hours = 0
            self.overtime_hours = 0

            # Calculate overtime/undertime
            if worked < expected_hours:
                self.undertime_hours = round(expected_hours - worked, 2)
                self.status = 'Half Day' if worked >= (expected_hours / 2) else 'Absent'
            elif worked > expected_hours:
                self.overtime_hours = round(worked - expected_hours, 2)

        elif self.status == "Clocked Out" and not self.time_out:
            raise ValueError("Cannot clock out without a valid 'time_out'.")

        super().save(*args, **kwargs)

    def mark_late(self):
        if self.time_in:
            standard_start_time = timezone.make_aware(
                timezone.datetime(self.date.year, self.date.month, self.date.day, 9, 0),
                timezone.get_current_timezone()
            )
            if self.time_in > standard_start_time:
                self.status = 'Late'
                self.late_hours = round((self.time_in - standard_start_time).total_seconds() / 3600, 2)
                self.save()

    def mark_undertime(self, expected_hours=8):
        if self.time_in and self.time_out:
            worked = (self.time_out - self.time_in).total_seconds() / 3600
            if worked < expected_hours:
                self.status = 'Half Day' if worked >= (expected_hours / 2) else 'Absent'
                self.undertime_hours = round(expected_hours - worked, 2)
                self.save()

    def mark_on_leave(self, leave_type="Paid"):
        self.status = "On Leave"
        self.holiday_type = leave_type
        self.save()

    class Meta:
        db_table = "attendance_tracking"
        verbose_name = "Attendance Tracking"
        verbose_name_plural = "Attendance Tracking"

    def __str__(self):
        return f'{self.employee} - {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
