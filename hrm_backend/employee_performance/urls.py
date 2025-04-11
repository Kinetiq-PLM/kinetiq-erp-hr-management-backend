from django.urls import path
from .views import (
    Employee_Performance_ListCreateAPIView,
    Employee_Performance_RetrieveUpdateDestroyAPIView,
)

app_name = 'employee_performance'

urlpatterns = [
    path('', Employee_Performance_ListCreateAPIView.as_view(), name = 'employee_performance_list_create'),
    path('<str:pk>/', Employee_Performance_RetrieveUpdateDestroyAPIView.as_view(), name = 'employee_performance_detail'),
]
