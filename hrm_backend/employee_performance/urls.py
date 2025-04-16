from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeePerformanceViewSet

router = DefaultRouter()
router.register(r'employee_performance', EmployeePerformanceViewSet)

app_name = 'employee_performance'

urlpatterns = [
    path('', include(router.urls)),
]
