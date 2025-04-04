from rest_framework import generics, status
from rest_framework.response import Response
from .models import Department
from .serializers import DepartmentSerializer

class DepartmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DepartmentDestroyAPIView(generics.DestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = 'dept_id'
