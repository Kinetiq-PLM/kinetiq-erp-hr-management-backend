from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.views import View
from .models import DepartmentSuperior

def department_superiors_view(request):
    department_superiors = DepartmentSuperior.objects.all()
    context = {
        'department_superiors': department_superiors
    }
    return render(request, 'admin/department_superiors/archived_department_superiors.html', context)

def archive_department_superior(request, pk):
    department_superior = get_object_or_404(DepartmentSuperior, pk=pk)
    department_superior.is_archived = True
    department_superior.save()
    messages.success(request, "Department Superior archived successfully.")
    return redirect(reverse('admin:department_superiors_departmentsuperior_changelist'))

def unarchive_department_superior(request, pk):
    department_superior = get_object_or_404(DepartmentSuperior, pk=pk)
    department_superior.is_archived = False
    department_superior.save()
    messages.success(request, "Department Superior unarchived successfully.")
    return redirect(reverse('department_superiors:archived_department_superiors'))
class ArchivedDepartmentSuperiorListView(View):
    def get(self, request):
        archived_superiors = DepartmentSuperior.objects.filter(is_archived=True)
        context = {
            'archived_department_superiors': archived_superiors
        }
        return render(request, 'admin/department_superiors/archived_department_superiors.html', context)
