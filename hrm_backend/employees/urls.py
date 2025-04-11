from django.urls import path
from .views import (
    Employee_ListCreateAPIView,
    Employee_RetrieveUpdateDestroyAPIView,
    Employee_ArchiveAPIView,
    Employee_UnarchiveAPIView,
    Employee_ArchiveListAPIView,
    Employee_HistoryView,
)

app_name = 'employees'

urlpatterns = [
    path('<str:pk>/archive/', Employee_ArchiveAPIView.as_view(), name = 'employee_archive'),
    path('<str:pk>/unarchive/', Employee_UnarchiveAPIView.as_view(), name = 'employees_unarchive'),
    path('archived/', Employee_ArchiveListAPIView.as_view(), name = 'archived_employees'),
    path('<str:employee_id>/history/', Employee_HistoryView.as_view(), name = 'employee-history-api'),
    path('', Employee_ListCreateAPIView.as_view(), name = 'employees_list_create'),
    path('<str:pk>/', Employee_RetrieveUpdateDestroyAPIView.as_view(), name = 'employee_detail'),
]
