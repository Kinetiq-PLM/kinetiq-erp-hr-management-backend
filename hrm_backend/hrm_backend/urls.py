from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/attendance_tracking/', include('attendance_tracking.urls', namespace = 'attendance_tracking')),
    path('api/departments/', include('departments.urls', )), 
    path('api/department_superiors/', include('department_superiors.urls', namespace = 'department_superiors')),
    path('api/employees/', include('employees.urls', namespace = 'employees')),
    path('api/employee_leave_requests/', include('employee_leave_requests.urls', namespace = 'employee_leave_requests')),
    path('api/employee_performance/', include('employee_performance.urls', namespace = 'employee_performance')),
    path('api/employee_salary/', include('employee_salary.urls', namespace = 'employee_salary')),
    path('api/positions/', include('positions.urls', namespace = 'positions')),
    path('api/workforce_allocation/', include('workforce_allocation.urls', namespace = 'workforce_allocation')),
   
    ]


