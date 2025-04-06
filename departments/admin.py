from django.contrib import admin
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
    list_display = ('dept_id', 'dept_name')
    search_fields = ('dept_id', 'dept_name')
    list_filter = (DepartmentFilter,)
