from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceScanView, AttendanceMarkedView, CustomLoginView
from .views import AttendanceTrackingViewSet

app_name = 'attendance_tracking'

router = DefaultRouter()
router.register(r'attendance_tracking', AttendanceTrackingViewSet, basename='attendance-tracking')

urlpatterns = [
    path('attendance/', AttendanceScanView.as_view(), name='attendance'),
    path('marked/', AttendanceMarkedView.as_view(), name='attendance_marked'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
