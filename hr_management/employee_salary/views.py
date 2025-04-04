from rest_framework import viewsets
from .models import EmployeeSalary
from .serializers import EmployeeSalarySerializer

class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
