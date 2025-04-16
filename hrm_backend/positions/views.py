from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Position
from .serializers import (
    Position_Serializer,
    Position_CreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('positions.view_position'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    lookup_field = 'pk'
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get_queryset(self):
        return Position.objects.filter(is_archived = False)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Position_CreateSerializer
        return Position_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail = True, methods = ['post'])
    def archive(self, request, pk = None):
        position = self.get_object()
        if position.is_archived:
            return Response({"detail": "Position already archived."}, status = status.HTTP_400_BAD_REQUEST)
        position.is_archived = True
        position.save()
        return Response({"detail": "Position archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, pk = None):
        position = self.get_object()
        if not position.is_archived:
            return Response({"detail": "Position is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        position.is_archived = False
        position.save()
        return Response({"detail": "Position unarchived successfully."}, status = status.HTTP_200_OK)

    @action(detail=False, methods = ['get'])
    def archived(self, request):
        archived_positions = Position.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_positions, many = True)
        return Response(serializer.data)
