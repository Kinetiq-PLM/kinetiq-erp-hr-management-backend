from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Employee_Performance
from .serializers import (
    Employee_Performance_Serializer,
    Employee_Performance_CreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employee_performance.view_employee_performance'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class EmployeePerformanceViewSet(viewsets.ModelViewSet):
    queryset = Employee_Performance.objects.all()
    lookup_field = 'performance_id'
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Employee_Performance_CreateSerializer
        return Employee_Performance_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
