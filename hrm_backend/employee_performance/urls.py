from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeePerformanceViewSet, EmployeePerformanceViewList

router = DefaultRouter()
router.register(r'employee-performance', EmployeePerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('employee-performance-view/', EmployeePerformanceViewList.as_view(), name='employee-performance-view'),
]
