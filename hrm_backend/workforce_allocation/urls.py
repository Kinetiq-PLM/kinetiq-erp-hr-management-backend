from django.urls import path
from .views import (
    Workforce_Allocation_ListCreateAPIView,
    Workforce_Allocation_RetrieveUpdateDestroyAPIView,
    Workforce_Allocation_ArchiveAPIView,
    Workforce_Allocation_UnarchiveAPIView,
    Workforce_Allocation_ArchiveListAPIView,
)

app_name = 'workforce_allocation'

urlpatterns = [

    path('<str:pk>/archive/', Workforce_Allocation_ArchiveAPIView.as_view(), name = 'workforce_allocation_archive'),
    path('<str:pk>/unarchive/', Workforce_Allocation_UnarchiveAPIView.as_view(), name = 'workforce_allocation_unarchive'),
    path('archived/', Workforce_Allocation_ArchiveListAPIView.as_view(), name = 'archived_workforce_allocations'),
    path('', Workforce_Allocation_ListCreateAPIView.as_view(), name = 'workforce_allocation_list_create'),
    path('<str:pk>/', Workforce_Allocation_RetrieveUpdateDestroyAPIView.as_view(), name = 'workforce_allocation_detail'),

]