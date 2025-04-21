from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet

router = DefaultRouter()
router.register(r'', EmployeeViewSet)

app_name = 'employees'
urlpatterns = [
    path('', include(router.urls)),
    path('archived/', EmployeeViewSet.as_view({'get': 'archived'}), name = 'archived-employees'),
]