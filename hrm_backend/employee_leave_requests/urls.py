from django.urls import path
from .views import (
    Employee_Leave_Request_ListCreateAPIView,
    Employee_Leave_Request_RetrieveUpdateDestroyAPIView,
    Employee_Leave_Request_ArchiveAPIView,
    Employee_Leave_Request_UnarchiveAPIView,
    Employee_Leave_Request_ArchiveListAPIView,
    Employee_Leave_Request_HistoryView,
)

app_name = 'leave_requests'

urlpatterns = [
    path('<str:leave_id>/archive/', Employee_Leave_Request_ArchiveAPIView.as_view(), name='leave_archive'),
    path('<str:leave_id>/unarchive/', Employee_Leave_Request_UnarchiveAPIView.as_view(), name='leave_unarchive'),
    path('archived/', Employee_Leave_Request_ArchiveListAPIView.as_view(), name='archived_leave_requests'),
    path('<str:leave_id>/history/', Employee_Leave_Request_HistoryView.as_view(), name='leave-history-api'),
    path('', Employee_Leave_Request_ListCreateAPIView.as_view(), name='leave_list_create'),
    path('<str:leave_id>/', Employee_Leave_Request_RetrieveUpdateDestroyAPIView.as_view(), name='leave_detail'),
]
