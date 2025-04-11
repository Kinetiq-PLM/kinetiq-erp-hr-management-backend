from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from rest_framework import viewsets, permissions
from .models import Employee
from .serializers import EmployeeSerializer
from django.views import View 

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('employees.view_employee')
    
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    serializer_class = EmployeeSerializer
    permission_classes = [IsHRMember]

def archive_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_archived = True
    employee.save()
    messages.success(request, "Employee archived successfully.")
    return redirect(reverse('admin:employees_employee_changelist'))

def unarchive_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_archived = False
    employee.save()
    messages.success(request, "Employee unarchived successfully.")
    return redirect(reverse('employees:archived_employees'))

class ArchivedEmployeeListView(View):
    def get(self, request):
        archived_employees = Employee.objects.filter(is_archived=True)
        context = {
            'archived_employees': archived_employees
        }
        return render(request, 'admin/employees/archived_employees.html', context)
    permission_classes = [permissions.AllowAny]
