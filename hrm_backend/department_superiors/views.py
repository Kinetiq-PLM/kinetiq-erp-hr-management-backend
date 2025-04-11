from rest_framework import generics, permissions, status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Department_Superior
from .serializers import (
    Department_Superior_Serializer,
    Department_Superior_WriteSerializer,
    Department_Superior_History_Serializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('department_superiors.view_departmentsuperior'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Department_Superior_ViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department_Superior.objects.select_related('position', 'dept').all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return Department_Superior_Serializer
        return Department_Superior_WriteSerializer
    
    def get_queryset(self):
        return Department_Superior.objects.filter(is_archived = False)
    
class Department_Superior_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department_Superior.objects.select_related('position', 'dept').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return Department_Superior_Serializer
        return Department_Superior_WriteSerializer
    
    def get_queryset(self):
        return Department_Superior.objects.filter(is_archived = False)

class Department_Superior_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department_Superior.objects.select_related('position', 'dept').all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return Department_Superior_Serializer
        return Department_Superior_WriteSerializer

class Department_Superior_DestroyAPIView(generics.DestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department_Superior.objects.select_related('position', 'dept').all()
    serializer_class = Department_Superior_Serializer
    lookup_field = 'dept_superior_id'

class Department_Superior_ArchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        department_superior = get_object_or_404(Department_Superior, pk = pk)
        if department_superior.is_archived:
            return Response({"detail": "Department Superior already archived."}, status = status.HTTP_400_BAD_REQUEST)
        department_superior.is_archived = True
        department_superior.save()
        return Response({"detail": "Department Superior archived successfully."}, status = status.HTTP_200_OK)

class Department_Superior_UnarchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        department_superior = get_object_or_404(Department_Superior, pk = pk)
        if not department_superior.is_archived:
            return Response({"detail": "Department Superior is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        department_superior.is_archived = False
        department_superior.save()
        return Response({"detail": "Department Superior unarchived successfully."}, status = status.HTTP_200_OK)

class Department_Superior_ArchiveListAPIView(generics.ListAPIView):
      # permission_classes = [IsAuthenticated, IsHRMember]
    serializer_class = Department_Superior_Serializer

    def get_queryset(self):
        return Department_Superior.objects.select_related('position', 'dept').filter(is_archived = True)
    

class Department_Superior_HistoryView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get(self, request, *args, **kwargs):
        dept_id = kwargs.get('dept_id')
        if dept_id:
            try:
                department_superior = Department_Superior.objects.get(dept_id = dept_id)
                history = department_superior.history.all()
                serializer = Department_Superior_History_Serializer(history, many = True)
                
                return Response(serializer.data, status = status.HTTP_200_OK)
            
            except Department_Superior.DoesNotExist:
                return Response({"detail": "Department Superior not found."}, status = status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Department Superior ID is required."}, status = status.HTTP_400_BAD_REQUEST)
