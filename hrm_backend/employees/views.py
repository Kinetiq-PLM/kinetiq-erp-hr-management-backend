from rest_framework import generics, permissions, status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Employee
from .serializers import (
    Employee_Serializer,
    Employee_History_Serializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employees.view_employees'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Employee_ViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, isHRMember]
    queryset = Employee.objects.all()
    serializer_class = Employee_Serializer

class Employee_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, isHRMember]
    queryset = Employee.objects.all()
    serializer_class = Employee_Serializer

    def get_queryset(self):
        return Employee.objects.filter(is_archived = False)

class Employee_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, isHRMember]
    queryset = Employee.objects.all()
    serializer_class = Employee_Serializer
    lookup_field = 'pk'

class Employee_DestroyAPIView(generics.DestroyAPIView):
    # permission_classes = [IsAuthenticated, isHRMember]
    queryset = Employee.objects.all()
    serializer_class = Employee_Serializer
    lookup_field = 'employee_id'

# ARCHIVE LOGIC 
class Employee_ArchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, isHRMember]

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        if employee.is_archived:
            return Response({"detail": "Employee already archived."}, status = status.HTTP_400_BAD_REQUEST)
        employee.is_archived = True
        employee.save()
        return Response({"detail": "Employee archived successfully."}, status = status.HTTP_200_OK)

class Employee_UnarchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, isHRMember]

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        if not employee.is_archived:
            return Response({"detail": "Employee is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        employee.is_archived = False
        employee.save()
        return Response({"detail": "Employee unarchived successfully."}, status = status.HTTP_200_OK)

class Employee_ArchiveListAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, isHRMember]
    serializer_class = Employee_Serializer

    def get_queryset(self):
        return Employee.objects.filter(is_archived = True)

class Employee_HistoryView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get(self, request, *args, **kwargs):
        dept_id = kwargs.get('dept_id')
        if dept_id:
            try:
                employee = Employee.objects.get(dept_id = dept_id)
                history = employee.history.all()
                serializer = Employee_History_Serializer(history, many = True)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response({"detail": "Employee not found."}, status = status.HTTP_404_NOT_FOUND)
        else:
             return Response({"detail": "Employee ID is required."}, status = status.HTTP_400_BAD_REQUEST)