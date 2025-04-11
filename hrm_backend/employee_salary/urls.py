from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeSalaryViewSet, get_employment_type

router = DefaultRouter()
router.register(r'employee_salary', EmployeeSalaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get_employment_type/', get_employment_type, name='get_employment_type'),
]
