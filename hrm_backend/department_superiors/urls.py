from django.urls import path
from .views import (
    Department_Superior_ListCreateAPIView,
    Department_Superior_RetrieveUpdateDestroyAPIView,
    Department_Superior_ArchiveAPIView,
    Department_Superior_UnarchiveAPIView,
    Department_Superior_ArchiveListAPIView,
    Department_Superior_HistoryView,
)

app_name = 'department_superiors'

urlpatterns = [
    path('<str:pk>/archive/', Department_Superior_ArchiveAPIView.as_view(), name = 'department_superior_archive'),
    path('<str:pk>/unarchive/', Department_Superior_UnarchiveAPIView.as_view(), name = 'department_superior_unarchive'),
    path('archived/', Department_Superior_ArchiveListAPIView.as_view(), name = 'archived_department_superiors'),
    path('<str:dept_superior_id>/history/', Department_Superior_HistoryView.as_view(), name = 'department_superior_history_api'),
    path('', Department_Superior_ListCreateAPIView.as_view(), name = 'department_superior_list_create'),
    path('<str:pk>/', Department_Superior_RetrieveUpdateDestroyAPIView.as_view(), name = 'department_superior_detail'),
]

