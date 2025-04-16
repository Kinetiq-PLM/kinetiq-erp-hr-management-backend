from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Department_Superior, Department
from .serializers import(
    Department_Superior_Serializer,
    Department_Superior_CreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('department_superiors.view_departmentsuperior'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Department_SuperiorViewSet(viewsets.ModelViewSet):
    queryset = Department_Superior.objects.select_related('position', 'dept', 'employee').all()
    serializer_class = Department_Superior_Serializer
    # permission_classes = [IsAuthenticated, IsHRMember]
    lookup_field = 'dept_superior_id'

    def get_queryset(self):
        return Department_Superior.objects.filter(is_archived = False)

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

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Department_Superior_CreateSerializer
        return Department_Superior_Serializer

    # added archive and unarchive functionsalities

    @action(detail = True, methods = ['post'])
    def archive(self, request, pk = None):
        department_superior = self.get_object()
        if department_superior.is_archived:
            return Response({"detail": "Department Superior already archived."}, status = status.HTTP_400_BAD_REQUEST)
        department_superior.is_archived = True
        department_superior.save()
        return Response({"detail": "Department Superior archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, pk = None):
        department_superior = self.get_object()
        if not department_superior.is_archived:
            return Response({"detail": "Department Superior is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        department_superior.is_archived = False
        department_superior.save()
        return Response({"detail": "Department Superior unarchived successfully."}, status = status.HTTP_200_OK)

    @action(detail = False, methods=['get'])
    def archived(self, request):
        archived_superiors = Department_Superior.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_superiors, many = True)
        return Response(serializer.data)
