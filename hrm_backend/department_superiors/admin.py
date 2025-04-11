from django.contrib import admin
from .models import DepartmentSuperior
from django.urls import reverse
from django.utils.html import format_html

@admin.register(DepartmentSuperior)
class DepartmentSuperiorAdmin(admin.ModelAdmin):
    list_display = (
        'dept_superior_id', # ADDED THIS BECAUSE THERE IS NO FUCKING PRIMARY KEy xd
        'get_dept_id',
        'get_dept_name',
        'get_position_id',
        'get_position_title',
        'get_employee_id',
        'get_superior_name',
        'get_phone',
        'get_employee_status',
        'hierarchy_level',
        'actions_column',
    )

    list_filter = ( 'dept_superior_id', 'dept',)
    search_fields = ('dept_superior_id', 'position__position_title',)
    list_display_links = None  # made ALL columns non-clickable (since we have custom edit button)

    # removed add department_superior button
    def has_add_permission(self, request):
        return False

    # added new columns which are not in initial table columns
    
    def get_dept_id(self, obj):
        return obj.dept.dept_id
    get_dept_id.short_description = 'Department ID'

    def get_dept_name(self, obj):
        return obj.dept.dept_name
    get_dept_name.short_description = 'Department Name'

    def get_position_id(self, obj):
        return obj.position.position_id
    get_position_id.short_description = 'Position ID'

    def get_employee_id(self, obj):
        return obj.get_employee_id()
    get_employee_id.short_description = 'Employee ID'

    def get_first_name(self, obj):
        return obj.get_first_name()
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.get_last_name()
    get_last_name.short_description = 'Last Name'

    def get_phone(self, obj):
        return obj.get_phone()
    get_phone.short_description = 'Phone'

    def get_employee_status(self, obj):
        return obj.get_employee_status()
    get_employee_status.short_description = 'Employee Status'

    # to make two names in one
    def get_superior_name(self, obj):
        first_name = obj.get_first_name()
        last_name = obj.get_last_name()
        return f"{first_name} {last_name}" if first_name and last_name else "N/A"
    get_superior_name.short_description = 'Superior Name'

    # for position title
    def get_position_title(self, obj):
        position_title = obj.position.position_title
        return position_title.replace("(Regular)", "").strip() if position_title else "-"
    get_position_title.short_description = 'Position Title'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_archived = False)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'is_archived' in fields:
            fields.remove('is_archived')
        return fields

    def actions_column(self, obj):
        edit_url = reverse('admin:department_superiors_departmentsuperior_change', args=[obj.pk])
        archive_url = reverse('department_superiors:department_superior_archive', args=[obj.pk])
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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['view_archived_url'] = reverse('department_superiors:archived_department_superiors')
        return super().changelist_view(request, extra_context=extra_context)