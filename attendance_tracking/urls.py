from django.urls import path
from .views import AttendanceListCreateAPIView, AttendanceUpdateAPIView

urlpatterns = [
    path('attendance/', AttendanceListCreateAPIView.as_view(), name='attendance-list-create'),
    path('attendance/<str:attendance_id>/', AttendanceUpdateAPIView.as_view(), name='attendance-update'),
]
