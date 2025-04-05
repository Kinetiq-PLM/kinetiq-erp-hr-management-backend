from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from employees.models import Employee
from rest_framework import viewsets
from .models import EmployeeSalary
from .serializers import EmployeeSalarySerializer


@login_required
@csrf_exempt
def get_employment_type(request):
    employee_id = request.GET.get('employee_id')
    if not employee_id:
        return JsonResponse({'error': 'No employee ID provided'}, status=400)

    try:
        employee = Employee.objects.get(employee_id=employee_id)
        return JsonResponse({'employment_type': employee.employment_type})
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
