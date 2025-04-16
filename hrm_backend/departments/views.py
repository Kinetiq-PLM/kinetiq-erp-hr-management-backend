from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Department
from .serializers import Department_Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('departments.view_departments'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = Department_Serializer
    # permission_classes = [IsAuthenticated, IsHRMember]
    lookup_field = 'dept_id'

    def get_queryset(self):
        return Department.objects.filter(is_archived = False)

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

    @action(detail = True, methods = ['post'])
    def archive(self, request, pk = None):
        department = self.get_object()
        if department.is_archived:
            return Response({"detail": "Department already archived."}, status = status.HTTP_400_BAD_REQUEST)
        department.is_archived = True
        department.save()
        return Response({"detail": "Department archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, pk = None):
        department = self.get_object()
        if not department.is_archived:
            return Response({"detail": "Department is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        department.is_archived = False
        department.save()
        return Response({"detail": "Department unarchived successfully."}, status = status.HTTP_200_OK)

    @action(detail = False, methods = ['get'])
    def archived(self, request):
        archived_departments = Department.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_departments, many = True)
        return Response(serializer.data)
