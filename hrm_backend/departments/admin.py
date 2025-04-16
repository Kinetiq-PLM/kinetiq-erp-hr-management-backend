from django.contrib import admin
from .models import Department
from django.urls import reverse
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter


# for filtering, some sub modules have these
class ActiveDepartment_Filter(SimpleListFilter):
    title = 'Department'
    parameter_name = 'dept'

    def lookups(self, request, model_admin):
        active_departments = Department.objects.filter(is_archived = False)
        return [(dept.pk, dept.dept_name) for dept in active_departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(dept__pk=self.value())
        return queryset

@admin.register(Department)
class Department_Admin(admin.ModelAdmin):
    list_display = ('dept_id_display', 'dept_name',)
    search_fields = ('dept_id', 'dept_name')
    list_filter = ('dept_name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_archived = False)

    def get_fields(self, request, obj = None):
        fields = super().get_fields(request, obj)
        if 'is_archived' in fields:
            fields.remove('is_archived')
        return fields

    def dept_id_display(self, obj):
        return mark_safe(f'{obj.dept_id}')
    dept_id_display.short_description = 'Department ID'