from django.urls import path
from .views import (
    Attendance_Tracking_ListCreateAPIView,
    Attendance_Tracking_RetrieveUpdateDestroyAPIView,
)
from .views import Barcode_ScanView

app_name = 'attendance_tracking'

urlpatterns = [
    path('scan/<str:employee_id>/', Barcode_ScanView.as_view(), name = 'barcode_scan'),
    path('', Attendance_Tracking_ListCreateAPIView.as_view(), name = 'attendance_tracking_list_create'),
    path('<str:pk>/', Attendance_Tracking_RetrieveUpdateDestroyAPIView.as_view(), name = 'attendance_tracking_detail'),
]
