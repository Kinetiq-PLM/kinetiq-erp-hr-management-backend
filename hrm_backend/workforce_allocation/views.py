from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Workforce_Allocation
from .serializers import (
    Workforce_Allocation_Serializer,
    Workforce_Allocation_CreateSerializer,
    Workforce_Allocation_RequestSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
import uuid

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('workforce_allocation.view_workforce_allocation'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Workforce_AllocationViewSet(viewsets.ModelViewSet):
    queryset = Workforce_Allocation.objects.select_related('employee', 'hr_approver').all()
    serializer_class = Workforce_Allocation_Serializer
    lookup_field = 'allocation_id'

    def get_queryset(self):
        return Workforce_Allocation.objects.filter(is_archived = False)

    def perform_create(self, serializer):
        allocation_id = f"ALLOC-{uuid.uuid4()}"
        request_id = f"REQ-{uuid.uuid4()}"
        serializer.save(allocation_id = allocation_id, request_id = request_id)

    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Workforce_Allocation_CreateSerializer
        elif self.action == 'request_workforce':
            return Workforce_Allocation_RequestSerializer
        return Workforce_Allocation_Serializer


    @action(detail = True, methods = ['post'])
    def archive(self, request, pk = None):
        workforce_allocation = self.get_object()
        if workforce_allocation.is_archived:
            return Response({"detail": "Workforce Allocation already archived."}, status = status.HTTP_400_BAD_REQUEST)
        workforce_allocation.is_archived = True
        workforce_allocation.save()
        return Response({"detail": "Workforce Allocation archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, pk = None):
        workforce_allocation = self.get_object()
        if not workforce_allocation.is_archived:
            return Response({"detail": "Workforce Allocation is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        workforce_allocation.is_archived = False
        workforce_allocation.save()
        return Response({"detail": "Workforce Allocation unarchived successfully."}, status = status.HTTP_200_OK)

    @action(detail = False, methods=['get'])
    def archived(self, request):
        archived_allocations = Workforce_Allocation.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_allocations, many = True)
        return Response(serializer.data)
    
    @action(detail = False, methods = ['post'])
    def request_workforce(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        instance = serializer.save()
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

