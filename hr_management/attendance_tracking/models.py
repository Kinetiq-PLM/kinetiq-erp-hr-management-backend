from django.db import models

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Late", "Late"),
        ("Half-Day", "Half-Day"),
        ("On Leave", "On Leave"),
    ]

    attendance_id = models.CharField(max_length=20, primary_key=True)
    employee_id = models.CharField(max_length=20, default="HR-EMP-0000")
    time_in = models.DateTimeField()
    time_out = models.DateTimeField(null=True, blank=True)
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Present")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_tracking"

    def __str__(self):
        return f"{self.employee_id} - {self.attendance_id}"

