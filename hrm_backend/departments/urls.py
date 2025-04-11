from django.urls import path
from .views import (
    Department_ListCreateAPIView,
    Department_RetrieveUpdateDestroyAPIView,
    Department_ArchiveAPIView,
    Department_UnarchiveAPIView,
    Department_ArchiveListAPIView,
    Department_HistoryView,
)

app_name = 'departments'

urlpatterns = [

    path('<str:pk>/archive/', Department_ArchiveAPIView.as_view(), name = 'department_archive'),
    path('<str:pk>/unarchive/', Department_UnarchiveAPIView.as_view(), name = 'department_unarchive'),
    path('archived/', Department_ArchiveListAPIView.as_view(), name = 'archived_departments'),
    path('<str:dept_id>/history/', Department_HistoryView.as_view(), name = 'departments-history-api'),
    path('', Department_ListCreateAPIView.as_view(), name = 'department_list_create'),
    path('<str:pk>/', Department_RetrieveUpdateDestroyAPIView.as_view(), name = 'department_detail'),
]