from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Overtime_Requests_ViewSet

app_name = 'overtime_requests'

router = DefaultRouter()
router.register(r'overtime_requests', Overtime_Requests_ViewSet, basename='overtime_requests')

urlpatterns = [
    path('', include(router.urls)),
]
