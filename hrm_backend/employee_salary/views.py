from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Employee_Salary
from .serializers import Employee_Salary_Serializer
# from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employee_salary.view_employee_salary'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Employee_Salary_ViewSet(viewsets.ModelViewSet):
     # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Salary.objects.all()
    serializer_class = Employee_Salary_Serializer

class Employee_Salary_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Salary.objects.all()
    serializer_class = Employee_Salary_Serializer

class Employee_Salary_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Salary.objects.all()
    serializer_class = Employee_Salary_Serializer
    lookup_field = 'pk'

class Employee_Salary_DestroyAPIView(generics.DestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Salary.objects.all()
    serializer_class = Employee_Salary_Serializer
    lookup_field = 'salary_id'