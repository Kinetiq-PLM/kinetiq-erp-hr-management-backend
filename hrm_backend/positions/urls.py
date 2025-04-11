from django.urls import path
from .views import (
    Position_ListCreateAPIView,
    Position_RetrieveUpdateDestroyAPIView,
    Position_ArchiveAPIView,
    Position_UnarchiveAPIView,
    Position_ArchiveListAPIView,
    Position_HistoryView,
)

app_name = 'positions'

urlpatterns = [
    path('<str:pk>/archive/', Position_ArchiveAPIView.as_view(), name = 'positions_archive'),
    path('<str:pk>/unarchive/', Position_UnarchiveAPIView.as_view(), name = 'positions_unarchive'),
    path('archived/', Position_ArchiveListAPIView.as_view(), name = 'archived_positions'),
    path('<str:position_id>/history/', Position_HistoryView.as_view(), name = 'position-history-api'),
    path('', Position_ListCreateAPIView.as_view(), name = 'positions_list_create'),
    path('<str:pk>/', Position_RetrieveUpdateDestroyAPIView.as_view(), name = 'position_detail'),
]
