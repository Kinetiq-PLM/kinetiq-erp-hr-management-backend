from django.contrib import admin
from .models import Employee
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id',
        'first_name',
        'last_name',
        'dept',
        'position',
        'employment_type',
        'status',
        'is_supervisor',
        'created_at',
        'updated_at',
        'actions_column',
    )

    list_filter = ('employment_type', 'status', 'is_supervisor')
    search_fields = ('first_name', 'last_name', 'employee_id', 'phone')
    readonly_fields = ('employee_id', 'created_at', 'updated_at')

    def department(self, obj):
        return obj.dept.name if obj.dept else 'N/A'

    def position(self, obj):
        return obj.position.title if obj.position else 'N/A'

    # just don't delete or edit any of these
    def actions_column(self, obj):
        edit_url = reverse('admin:employees_employee_change', args=[obj.pk])
        archive_url = reverse('employees:employee_archive', args=[obj.pk])
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_archived=False)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['view_archived_url'] = reverse('employees:archived_employees')
        return super().changelist_view(request, extra_context=extra_context)