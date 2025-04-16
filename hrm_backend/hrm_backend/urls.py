from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/attendance_tracking/', include('attendance_tracking.urls', namespace = 'attendance_tracking')),
    path('api/calendar_dates/', include('calendar_dates.urls', namespace = 'calendar_dates')),
    path('api/candidates/', include('candidates.urls', namespace = 'candidates')),
    path('api/departments/', include('departments.urls', )), 
    path('api/department_superiors/', include('department_superiors.urls', namespace = 'department_superiors')),
    path('api/employees/', include('employees.urls', namespace = 'employees')),
    path('api/employee_leave_balances/', include('employee_leave_balances.urls', namespace = 'employee_leave_balances')),
    path('api/employee_leave_requests/', include('employee_leave_requests.urls', namespace = 'employee_leave_requests')),
    path('api/employee_performance/', include('employee_performance.urls', namespace = 'employee_performance')),
    path('api/employee_salary/', include('employee_salary.urls', namespace = 'employee_salary')),
    path('api/job_posting/', include('job_posting.urls', namespace = 'job_posting')),
    path('api/positions/', include('positions.urls', namespace = 'positions')),
    path('api/payroll/', include('payroll.urls', namespace = 'payroll')),
    path('api/resignation/', include('resignation.urls', namespace = 'resignation')),
    path('api/workforce_allocation/', include('workforce_allocation.urls', namespace = 'workforce_allocation')),
   
    ]


