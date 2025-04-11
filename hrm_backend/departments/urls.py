from django.urls import path
from .views import (
    DepartmentListCreateAPIView,
    DepartmentRetrieveUpdateDestroyAPIView,
    archive_department,
    unarchive_department,
    ArchivedDepartmentListView
)

app_name = 'departments'

urlpatterns = [
    # added endpoints i forgot 
    path('', DepartmentListCreateAPIView.as_view(), name='department_list_create'),
    path('<str:pk>/', DepartmentRetrieveUpdateDestroyAPIView.as_view(), name='department_detail'),

    # Archive-related views
    path('<str:pk>/archive/', archive_department, name='department_archive'),
    path('<str:pk>/unarchive/', unarchive_department, name='department_unarchive'),
    path('archived/', ArchivedDepartmentListView.as_view(), name='archived_departments'),
]
