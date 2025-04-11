from django.db import models
from employees.models import Employee

class Attendance_Tracking(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Clocked Out", "Clocked Out"),
        ("Absent", "Absent"),
        ("On Leave", "On Leave"),
        ("Late", "Late"),
        ("Half Day", "Half Day"),
    ]

    def get_default_employee():
        return Employee.objects.get(employee_id = "HR-EMP-0000").id

    attendance_id = models.CharField(max_length = 20, primary_key = True)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, related_name = "attendances", default = get_default_employee)
    date = models.DateField()
    time_in = models.DateTimeField()
    time_out = models.DateTimeField(null = True, blank = True)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = "Present")
    late_hours = models.DecimalField(max_digits = 4, decimal_places = 2, default = 0)
    undertime_hours = models.DecimalField(max_digits = 4, decimal_places = 2, default = 0)
    is_holiday = models.BooleanField(default = False)
    holiday_type = models.CharField(max_length = 20, null = True, blank = True)
    # work_hours = models.DecimalField(max_digits = 5, decimal_places=2, null = True, blank = True) commented out since auto generated ni DB
    created_at = models.DateTimeField(auto_now = True)
    updated_at = models.DateTimeField(auto_now = True)
    is_archived = models.BooleanField(default = False)

    class Meta:
        db_table = "attendance_tracking"
        verbose_name = "Attendance Tracking" # added para maganda tignan sa admin
        verbose_name_plural = "Attendance Tracking"

    def __str__(self):
        return f"{self.employee_id} - {self.attendance_id}"

