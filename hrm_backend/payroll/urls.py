from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayrollViewSet

router = DefaultRouter()
router.register(r'payrolls', PayrollViewSet)

app_name = 'payroll'

urlpatterns = [
    path('', include(router.urls)),
]
