from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Employee_Leave_Request
from .serializers import (
    Employee_Leave_Request_Serializer,
    Employee_Leave_Request_CreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('human_resources.view_leaverequest'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Employee_Leave_Request_ViewSet(viewsets.ModelViewSet):
    queryset = Employee_Leave_Request.objects.all()
    lookup_field = 'leave_id'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Employee_Leave_Request_CreateSerializer
        return Employee_Leave_Request_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail =True, methods = ['post'])
    def archive(self, request, leave_id = None):
        leave = self.get_object()
        if leave.status == "Archived":
            return Response({"detail": "Leave request already archived."}, status = status.HTTP_400_BAD_REQUEST)
        leave.status = "Archived"
        leave.save()
        return Response({"detail": "Leave request archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, leave_id = None):
        leave = self.get_object()
        if leave.status != "Archived":
            return Response({"detail": "Leave request is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        leave.status = "Pending"
        leave.save()
        return Response({"detail": "Leave request unarchived successfully."}, status = status.HTTP_200_OK)
    
    @action(detail = False, methods=['get'])
    def archived(self, request):
        archived_leave_requests = Employee_Leave_Request.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_leave_requests, many = True)
        return Response(serializer.data)
