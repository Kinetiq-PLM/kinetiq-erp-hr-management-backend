from rest_framework import viewsets, permissions
from .models import Position
from .serializers import PositionSerializer

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('positions.view_position')

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all().order_by('-created_at')
    serializer_class = PositionSerializer
    permission_classes = [permissions.AllowAny]
