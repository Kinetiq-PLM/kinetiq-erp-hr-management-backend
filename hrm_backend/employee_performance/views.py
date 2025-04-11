from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Employee_Performance
from .serializers import Employee_Performance_Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employee_performance.view_employee_performance'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True
        
class Employee_Performance_ViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Performance.objects.all()
    serializer_class = Employee_Performance_Serializer

class Employee_Performance_ListCreateAPIView(generics.ListCreateAPIView):
     # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Performance.objects.all()
    serializer_class = Employee_Performance_Serializer

class Employee_Performance_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
     # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Performance.objects.all()
    serializer_class = Employee_Performance_Serializer
    lookup_field = 'pk'

class Employee_Performance_DestroyAPIView(generics.DestroyAPIView):
     # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Employee_Performance.objects.all()
    serializer_class = Employee_Performance_Serializer
    lookup_field = 'performance_id'