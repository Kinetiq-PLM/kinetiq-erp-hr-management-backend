from django.contrib import admin
from django.urls import path, include
from department_superiors import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/departments/', include('departments.urls', namespace='departments')),
    path('api/positions/', include('positions.urls', namespace='positions')),
    path('api/department_superiors/', views.department_superiors_view, name='department_superiors'),
    path('api/employees/', include('employees.urls', namespace='employees')),
]
