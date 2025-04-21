from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Department_Superior, 
    Department,
)
from positions.models import Position
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
    queryset = Department_Superior.objects.select_related('position', 'dept').all()
    serializer_class = Department_Superior_Serializer
    # permission_classes = [IsAuthenticated, IsHRMember]
    lookup_field = 'dept_superior_id'

    def get_queryset(self):
        if self.action in ['unarchive', 'retrieve'] or self.request.path.endswith('/unarchive/'):
            return Department_Superior.objects.all()
        
        return Department_Superior.objects.filter(is_archived = False)

    def perform_create(self, serializer):
        dept_name = self.request.data.get('dept_name', None)
        position_title = self.request.data.get('position_title', None)
        department = None
        if dept_name:
            try:
                department = Department.objects.get(dept_name = dept_name)
            except Department.DoesNotExist:
                raise PermissionDenied(f"Department '{dept_name}' does not exist.")
        
        position = None
        if position_title:
            position = Position.objects.filter(
                position_title = position_title, 
                is_archived = False
            ).first()
            
            if not position:
                position = Position.objects.filter(position_title = position_title).first()
                
            if not position:
                raise PermissionDenied(f"Position '{position_title}' does not exist.")
        
        serializer.save(dept = department, position = position)

    def perform_update(self, serializer):
        dept_name = self.request.data.get('dept_name', None)
        position_title = self.request.data.get('position_title', None)
        update_fields = {}
        
        if dept_name:
            try:
                department = Department.objects.get(dept_name = dept_name)
                update_fields['dept'] = department
            except Department.DoesNotExist:
                raise PermissionDenied(f"Department '{dept_name}' does not exist.")
                
        if position_title:
            position = Position.objects.filter(
                position_title = position_title, 
                is_archived = False
            ).first()
            
            if not position:
                position = Position.objects.filter(position_title = position_title).first()
                
            if position:
                update_fields['position'] = position
            else:
                raise PermissionDenied(f"Position '{position_title}' does not exist.")
        
        serializer.save(**update_fields)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Department_Superior_CreateSerializer
        return Department_Superior_Serializer

    @action(detail = True, methods = ['post'])
    def archive(self, request, dept_superior_id = None):
        department_superior = self.get_object()
        if department_superior.is_archived:
            return Response({"detail": "Department Superior already archived."}, status = status.HTTP_400_BAD_REQUEST)
        department_superior.is_archived = True
        department_superior.save()
        return Response({"detail": "Department Superior archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, dept_superior_id = None):
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