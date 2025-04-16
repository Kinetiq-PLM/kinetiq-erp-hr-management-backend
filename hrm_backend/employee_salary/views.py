from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Employee_Salary
from .serializers import (
    Employee_Salary_Serializer,
    Employee_Salary_CreateSerializer
)

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employee_salary.view_employee_salary'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = Employee_Salary.objects.all()
    lookup_field = 'salary_id'
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Employee_Salary_CreateSerializer
        return Employee_Salary_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
