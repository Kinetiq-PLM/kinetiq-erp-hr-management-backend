from django.urls import path
from .views import DepartmentListCreateAPIView, DepartmentDestroyAPIView

urlpatterns = [
    path('departments/', DepartmentListCreateAPIView.as_view(), name = 'department-list-create'),
    path('departments/<str:dept_id>/', DepartmentDestroyAPIView.as_view(), name = 'department-delete'),
]
