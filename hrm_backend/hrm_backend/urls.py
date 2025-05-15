from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from attendance_tracking.views import AttendanceScanView, AttendanceMarkedView, CustomLoginView

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('', health_check),

    path('admin/', admin.site.urls),
    
    path('attendance/', AttendanceScanView.as_view(), name='attendance'),
    path('marked/', AttendanceMarkedView.as_view(), name='attendance_marked'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='attendance/logout.html'), name='logout'),

    path('api/attendance_tracking/', include('attendance_tracking.urls', namespace='attendance_tracking')),
    path('api/calendar_dates/', include('calendar_dates.urls', namespace='calendar_dates')),
    path('api/candidates/', include('candidates.urls', namespace='candidates')),
    path('api/dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('api/departments/', include('departments.urls')),
    path('api/department_superiors/', include('department_superiors.urls', namespace='department_superiors')),
    path('api/employees/', include('employees.urls', namespace='employees')),
    path('api/employee_leave_balances/', include('employee_leave_balances.urls', namespace='employee_leave_balances')),
    path('api/employee_leave_requests/', include('employee_leave_requests.urls', namespace='employee_leave_requests')),
    path('api/employee_performance/', include('employee_performance.urls', namespace='employee_performance')),
    path('api/employee_salary/', include('employee_salary.urls', namespace='employee_salary')),
    path('api/job_posting/', include('job_posting.urls', namespace='job_posting')),
    path('api/positions/', include('positions.urls', namespace='positions')),
    path('api/payroll/', include('payroll.urls', namespace='payroll')),
    path('api/resignation/', include('resignation.urls', namespace='resignation')),
    path('api/workforce_allocation/', include('workforce_allocation.urls', namespace='workforce_allocation')),
    path('api/overtime_requests/', include('overtime_requests.urls', namespace='overtime_requests')),
    path('api/interviews/', include('interviews.urls', namespace='interviews')),
    path('api/onboarding/', include('onboarding.urls', namespace='onboarding')),

    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
