from django.contrib import admin
from .models import Calendar_Date

@admin.register(Calendar_Date)
class Calendar_Date_Admin(admin.ModelAdmin):
    list_display = ('date', 'is_workday', 'is_holiday', 'is_special', 'holiday_name')
    search_fields = ('date', 'holiday_name')
    list_filter = ('is_workday', 'is_holiday', 'is_special')
