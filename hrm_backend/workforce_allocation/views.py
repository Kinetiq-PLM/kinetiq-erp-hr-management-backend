from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import Workforce_Allocation
from .serializers import Workforce_Allocation_Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('workforce_allocation.view_workforce_allocation'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Workforce_Allocation_ViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Workforce_Allocation.objects.all()
    serializer_class = Workforce_Allocation_Serializer

    def get_queryset(self):
        return Workforce_Allocation.objects.filter(is_archived = False)

class Workforce_Allocation_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Workforce_Allocation.objects.all()
    serializer_class = Workforce_Allocation_Serializer

    def get_queryset(self):
        return Workforce_Allocation.objects.filter(is_archived = False)

class Workforce_Allocation_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Workforce_Allocation.objects.all()
    serializer_class = Workforce_Allocation_Serializer
    lookup_field = 'pk'

class Workforce_Allocation_DestroyAPIView(generics.DestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Workforce_Allocation.objects.all()
    serializer_class = Workforce_Allocation_Serializer
    lookup_field = 'dept_id'

# ARCHIVE LOGIC 
class Workforce_Allocation_ArchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        workforce_allocation = get_object_or_404(Workforce_Allocation, pk = pk)
        if workforce_allocation.is_archived:
            return Response({"detail": "Workforce already archived."}, status = status.HTTP_400_BAD_REQUEST)
        workforce_allocation.is_archived = True
        workforce_allocation.save()
        return Response({"detail": "Workforce archived successfully."}, status = status.HTTP_200_OK)

class Workforce_Allocation_UnarchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        workforce_allocation = get_object_or_404(Workforce_Allocation, pk = pk)
        if not workforce_allocation.is_archived:
            return Response({"detail": "Workforce is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        workforce_allocation.is_archived = False
        workforce_allocation.save()
        return Response({"detail": "Workforce unarchived successfully."}, status = status.HTTP_200_OK)

class Workforce_Allocation_ArchiveListAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    serializer_class = Workforce_Allocation_Serializer

    def get_queryset(self):
        return Workforce_Allocation.objects.filter(is_archived = True)
