from django.contrib import admin
from .models import Position

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'position_id', 'position_title', 'salary_grade', 'employment_type',
        'min_salary', 'max_salary', 'typical_duration_days', 'is_active',
        'created_at', 'updated_at'
    )
    list_filter = ('employment_type', 'is_active')
    search_fields = ('position_title', 'position_id', 'salary_grade')
    readonly_fields = ('position_id', 'created_at', 'updated_at')
