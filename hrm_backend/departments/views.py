from rest_framework import generics, permissions, status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Department
from .serializers import (
    Department_Serializer,
    Department_History_Serializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('departments.view_departments'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Department_ViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department.objects.all()
    serializer_class = Department_Serializer

    def get_queryset(self):
        return Department.objects.filter(is_archived = False)

class Department_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department.objects.all()
    serializer_class = Department_Serializer

    def get_queryset(self):
        return Department.objects.filter(is_archived = False)

class Department_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department.objects.all()
    serializer_class = Department_Serializer
    lookup_field = 'pk'

class Department_DestroyAPIView(generics.DestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Department.objects.all()
    serializer_class = Department_Serializer
    lookup_field = 'dept_id'

# ARCHIVE LOGIC 
class Department_ArchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        department = get_object_or_404(Department, pk = pk)
        if department.is_archived:
            return Response({"detail": "Department already archived."}, status = status.HTTP_400_BAD_REQUEST)
        department.is_archived = True
        department.save()
        return Response({"detail": "Department archived successfully."}, status = status.HTTP_200_OK)

class Department_UnarchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, pk):
        department = get_object_or_404(Department, pk = pk)
        if not department.is_archived:
            return Response({"detail": "Department is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        department.is_archived = False
        department.save()
        return Response({"detail": "Department unarchived successfully."}, status = status.HTTP_200_OK)

class Department_ArchiveListAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    serializer_class = Department_Serializer

    def get_queryset(self):
        return Department.objects.filter(is_archived = True)


# history for each departments
class Department_HistoryView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get(self, request, *args, **kwargs):
        dept_id = kwargs.get('dept_id')
        if dept_id:
            try:
                department = Department.objects.get(dept_id = dept_id)
                history = department.history.all()
                serializer = Department_History_Serializer(history, many = True)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except Department.DoesNotExist:
                return Response({"detail": "Department not found."}, status = status.HTTP_404_NOT_FOUND)
        else:
             return Response({"detail": "Department ID is required."}, status = status.HTTP_400_BAD_REQUEST)