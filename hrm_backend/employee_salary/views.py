from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
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
    # permission_classes = [permissions.IsAuthenticated, IsHRMember]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__employee_id']
    ordering_fields = ['effective_date', 'base_salary', 'daily_rate']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Employee_Salary_CreateSerializer
        return Employee_Salary_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail = False, methods = ['get'], url_path = 'history/(?P<employee_id>[^/.]+)')
    def salary_history(self, request, employee_id=None):
        salaries = self.queryset.filter(employee__employee_id = employee_id).order_by('-effective_date')
        serializer = self.get_serializer(salaries, many = True)
        return Response(serializer.data)
