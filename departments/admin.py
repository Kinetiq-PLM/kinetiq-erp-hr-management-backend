from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from .models import Department


# added list filtering (2 only ? if there's more then add below the next one (Dept_id), edit the fkign lookups and queryset)
class DepartmentFilter(admin.SimpleListFilter):
    title = 'Filter by'
    parameter_name = 'filter_by'

    def lookups(self, request, model_admin):
        return (
            ('dept_name', 'Department Name'),
            ('dept_id', 'Department ID'),
        )

    def queryset(self, request, queryset):
        filter_by = self.value()
        if filter_by == 'dept_name':
            return queryset.order_by('dept_name')
        if filter_by == 'dept_id':
            return queryset.order_by('dept_id')
        return queryset


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dept_id_display', 'dept_name', 'actions_column') # added new display, columns vertical dots
    list_display_links = None  # made ALL columns non-clickable (since we have custom edit button)
    search_fields = ('dept_id', 'dept_name')
    list_filter = (DepartmentFilter,)

    # is_archived check button hide
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_archived = False)

    # remove 'is_archived' from admin form (so it won't show in form fields) ewan bat nag appear wahahaha
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'is_archived' in fields:
            fields.remove('is_archived')
        return fields

    def dept_id_display(self, obj):
        return mark_safe(f'{obj.dept_id}') 

    dept_id_display.short_description = 'Department ID'

    def changelist_view(self, request, extra_context = None):
        extra_context = extra_context or {}
        extra_context['view_archived_url'] = reverse('departments:archived_departments')
        return super().changelist_view(request, extra_context=extra_context)

    # 3 vertical dots
    def actions_column(self, obj):
        edit_url = reverse('admin:departments_department_change', args = [obj.pk])
        archive_url = reverse('departments:department_archive', args = [obj.pk])

        return format_html(
            '''
            <div style="text-align: right;">
                <span style="cursor: pointer;">⋮</span>
                <div style="display: inline-block; margin-left: 5px;">
                    <a href = "{}">Edit</a> | 
                    <a href = "{}">Archive</a>
                </div>
            </div>
            ''',
            edit_url,
            archive_url
        )

    actions_column.short_description = ''

