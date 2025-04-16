from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet

router = DefaultRouter()
router.register(r'attendance_tracking', AttendanceViewSet)

app_name = 'attendance_tracking'

urlpatterns = [
    path('', include(router.urls)),
]
