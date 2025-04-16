from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Employee,
    Department,
)
from .serializers import (
    Employee_Serializer,

)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employees.view_employees'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = Employee_Serializer
    # permission_classes = [IsAuthenticated, IsHRMember]
    lookup_field = 'employee_id'

    def get_queryset(self):
        return Employee.objects.filter(is_archived = False)

    def perform_create(self, serializer):
        dept_name = self.request.data.get('dept_name', None)
        if dept_name:
            department = Department.objects.get(dept_name = dept_name)
            serializer.save(dept = department)
        else:
            serializer.save()

    def perform_update(self, serializer):
        dept_name = self.request.data.get('dept_name', None)
        if dept_name:
            department = Department.objects.get(dept_name = dept_name)
            serializer.save(dept = department)
        else:
            serializer.save()

    # added archive and unarchive functionsalities

    @action(detail = True, methods = ['post'])
    def archive(self, request, pk = None):
        employee = self.get_object()
        if employee.is_archived:
            return Response({"detail": "Employee already archived."}, status = status.HTTP_400_BAD_REQUEST)
        employee.is_archived = True
        employee.save()
        return Response({"detail": "Employee archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods=['post'])
    def unarchive(self, request, pk = None):
        employee = self.get_object()
        if not employee.is_archived:
            return Response({"detail": "Employee is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        employee.is_archived = False
        employee.save()
        return Response({"detail": "Employee unarchived successfully."}, status = status.HTTP_200_OK)

    @action(detail = False, methods=['get'])
    def archived(self, request):
        archived_employees = Employee.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_employees, many = True)
        return Response(serializer.data)
