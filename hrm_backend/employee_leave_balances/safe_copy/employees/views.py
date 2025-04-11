from rest_framework import viewsets, permissions
from .models import Employee
from .serializers import EmployeeSerializer

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('employees.view_employee')

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.AllowAny]
