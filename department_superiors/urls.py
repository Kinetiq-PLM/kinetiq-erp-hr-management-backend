from django.urls import path
from .views import (
    DepartmentSuperiorListCreateAPIView,
    DepartmentSuperiorDestroyAPIView,
)

urlpatterns = [
    path('department_superiors/', DepartmentSuperiorListCreateAPIView.as_view(), name='department-superior-list-create'),
    path('department_superiors/<str:dept_id>/<str:superior_job_title>/', DepartmentSuperiorDestroyAPIView.as_view(), name='department-superior-delete'),
]
