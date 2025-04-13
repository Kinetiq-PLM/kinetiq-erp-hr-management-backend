from django.contrib import admin
from django import forms
from .models import Department_Superior
from departments.models import Department
from django.contrib.admin import SimpleListFilter

# filtering don't remove (all of them are the same on all submodules) 
class ActiveDepartment_Filter(SimpleListFilter):
    title = 'Department'
    parameter_name = 'dept'

    def lookups(self, request, model_admin):
        active_departments = Department.objects.filter(is_archived = False)
        return [(dept.pk, dept.dept_name) for dept in active_departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(dept__pk = self.value())
        return queryset

@admin.register(Department_Superior)
class Department_Superior_Admin(admin.ModelAdmin):
    list_display = (
        'dept_superior_id', # ADDED THIS BECAUSE THERE IS NO FUCKING PRIMARY KEy xd
        'get_dept_name',
        'get_position_id',
        'get_position_title',
        'get_employee_id',
        'get_superior_name',
        'get_phone',
        'get_employee_status',
        'hierarchy_level',
    )

    list_filter = (ActiveDepartment_Filter,)
    search_fields = ('dept_superior_id', 'position__position_title',)
    # list_display_links = None

    def has_add_permission(self, request):
        return False

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

    def get_superior_name(self, obj):
        first_name = obj.get_first_name()
        last_name = obj.get_last_name()
        return f"{first_name} {last_name}" if first_name and last_name else "-"
    get_superior_name.short_description = 'Superior Name'

    def get_position_title(self, obj):
        position_title = obj.position.position_title
        return position_title.replace("(Regular)", "").strip() if position_title else "-"
    get_position_title.short_description = 'Position Title'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(dept__is_archived = False, is_archived = False)

    def get_fields(self, request, obj = None):
        fields = super().get_fields(request, obj)
        if 'is_archived' in fields:
            fields.remove('is_archived')
        return fields
    
# nilagyan ko na rin akhit walang add, just incase 
    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if obj is None:
            form.base_fields['change_reason'].required = False
            form.base_fields['change_reason'].widget = forms.HiddenInput()
        return form
