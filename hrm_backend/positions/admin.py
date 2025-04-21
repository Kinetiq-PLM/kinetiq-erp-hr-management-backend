from django.contrib import admin
from .models import Position

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'position_id',
        'position_title',
        'salary_grade',
        'min_salary',
        'max_salary', 
        'employment_type',
        'typical_duration_days', 
        'is_active',
        'created_at', 
        'updated_at',
        'is_archived',
    )
    list_filter = ('employment_type', 'is_active')
    # list_display_links = None
    search_fields = ('position_title', 'position_id', 'salary_grade')
    readonly_fields = ('position_id', 'created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_archived = False)

    def get_fields(self, request, obj = None):
        fields = super().get_fields(request, obj)
        if 'is_archived' in fields:
            fields.remove('is_archived')
        return fields