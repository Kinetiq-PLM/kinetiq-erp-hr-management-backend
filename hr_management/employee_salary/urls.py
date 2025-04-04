from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeSalaryViewSet

router = DefaultRouter()
router.register(r'employee_salary', EmployeeSalaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
