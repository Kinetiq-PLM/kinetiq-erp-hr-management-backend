from django.contrib import admin
from .models import DepartmentSuperior

@admin.register(DepartmentSuperior)
class DepartmentSuperiorAdmin(admin.ModelAdmin):
    list_display = ('dept_id', 'superior_job_title', 'hierarchy_level')
    list_filter = ('hierarchy_level',)
    search_fields = ('dept_id', 'superior_job_title')
    readonly_fields = ('dept_id', 'superior_job_title')
