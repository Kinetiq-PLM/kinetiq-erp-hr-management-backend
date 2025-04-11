from rest_framework import generics, permissions, status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Position
from .serializers import (
    Position_Serializer,
    Position_History_Serializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('positions.view_positions'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Position_ViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Position.objects.all()
    serializer_class = Position_Serializer

    def get_queryset(self):
        return Position.objects.filter(is_archived = False)

class Position_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Position.objects.all()
    serializer_class = Position_Serializer

    def get_queryset(self):
        return Position.objects.filter(is_archived = False)

class Position_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Position.objects.all()
    serializer_class = Position_Serializer
    lookup_field = 'pk'

class Position_DestroyAPIView(generics.DestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Position.objects.all()
    serializer_class = Position_Serializer
    lookup_field = 'position_id'

# ARCHIVE LOGIC 
class Position_ArchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        position = get_object_or_404(Position, pk = pk)
        if position.is_archived:
            return Response({"detail": "Position already archived."}, status = status.HTTP_400_BAD_REQUEST)
        position.is_archived = True
        position.save()
        return Response({"detail": "Position archived successfully."}, status = status.HTTP_200_OK)

class Position_UnarchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        position = get_object_or_404(Position, pk = pk)
        if not position.is_archived:
            return Response({"detail": "Position is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        position.is_archived = False
        position.save()
        return Response({"detail": "Position unarchived successfully."}, status = status.HTTP_200_OK)

class Position_ArchiveListAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    serializer_class = Position_Serializer

    def get_queryset(self):
        return Position.objects.filter(is_archived = True)

# history for each positions
class Position_HistoryView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get(self, request, *args, **kwargs):
        dept_id = kwargs.get('dept_id')
        if dept_id:
            try:
                positions = Position.objects.get(dept_id = dept_id)
                history = positions.history.all()
                serializer = Position_History_Serializer(history, many = True)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except Position.DoesNotExist:
                return Response({"detail": "Position not found."}, status = status.HTTP_404_NOT_FOUND)
        else:
             return Response({"detail": "Position ID is required."}, status = status.HTTP_400_BAD_REQUEST)