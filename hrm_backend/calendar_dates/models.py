from django.db import models

class Calendar_Date(models.Model):
    date = models.DateField(primary_key = True)
    is_workday = models.BooleanField()
    is_holiday = models.BooleanField(default = False)
    is_special = models.BooleanField(default = False)
    holiday_name = models.CharField(max_length = 100, null = True, blank = True)

    @staticmethod
    def check_is_holiday(date):
        try:
            calendar_date = Calendar_Date.objects.get(date = date)
            return calendar_date.is_holiday
        except Calendar_Date.DoesNotExist:
            return False

    @staticmethod
    def check_is_special(date):
        try:
            calendar_date = Calendar_Date.objects.get(date = date)
            return calendar_date.is_special
        except Calendar_Date.DoesNotExist:
            return False

    @staticmethod
    def check_is_workday(date):
        try:
            calendar_date = Calendar_Date.objects.get(date = date)
            return calendar_date.is_workday
        except Calendar_Date.DoesNotExist:
            return False

    def __str__(self):
        return f"{self.date} - Workday: {self.is_workday}"

    class Meta:
        db_table = 'calendar_dates'
        verbose_name = "Calendar Dates"
        verbose_name_plural = "Calendar Dates"
