from django.contrib import admin
from .models import Position
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'position_id',
        'position_title',
        'salary_grade',
        'employment_type',
        'min_salary',
        'max_salary', 
        'typical_duration_days', 
        'is_active',
        'created_at', 
        'updated_at',
        'actions_column',
    )
    list_filter = ('employment_type', 'is_active')
    list_display_links = None  # made ALL columns non-clickable (since we have custom edit button)
    search_fields = ('position_title', 'position_id', 'salary_grade')
    readonly_fields = ('position_id', 'created_at', 'updated_at')

    # added new colums for edit and archive

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_archived=False)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'is_archived' in fields:
            fields.remove('is_archived')
        return fields

    def actions_column(self, obj):
        edit_url = reverse('admin:positions_position_change', args=[obj.pk])
        archive_url = reverse('positions:positions_archive', args=[obj.pk])
        return format_html(
            '''
            <div style="text-align: right;">
                <span style="cursor: pointer;">⋮</span>
                <div style="display: inline-block; margin-left: 5px;">
                    <a href="{}">Edit</a> | 
                    <a href="{}">Archive</a>
                </div>
            </div>
            ''',
            edit_url,
            archive_url
        )

    actions_column.short_description = 'Actions'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['view_archived_url'] = reverse('positions:archived_positions')
        return super().changelist_view(request, extra_context=extra_context)
