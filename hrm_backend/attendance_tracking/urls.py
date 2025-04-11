from django.urls import path
from .views import AttendanceListCreateAPIView, AttendanceUpdateAPIView
from . import views

urlpatterns = [
    path('attendance/', AttendanceListCreateAPIView.as_view(), name='attendance-list-create'),
    path('attendance/<str:attendance_id>/', AttendanceUpdateAPIView.as_view(), name='attendance-update'),
    path('api/department_superiors/', views.department_superiors_view, name='department_superiors'),
]
