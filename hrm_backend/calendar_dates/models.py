from django.db import models

class Calendar_Date(models.Model):
    date = models.DateField(primary_key = True)
    is_workday = models.BooleanField()
    is_holiday = models.BooleanField(default = False)
    is_special = models.BooleanField(default = False)
    holiday_name = models.CharField(max_length = 100, null = True, blank = True)

    def __str__(self):
        return f"{self.date} - Workday: {self.is_workday}"

    class Meta:
        db_table = 'calendar_dates'
        verbose_name = "Calendar Dates" # added para maganda tignan sa admin
        verbose_name_plural = "Calendar Dates"
