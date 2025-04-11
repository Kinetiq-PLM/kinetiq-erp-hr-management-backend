from django.urls import path
from .views import (
    Employee_Salary_ListCreateAPIView,
    Employee_Salary_RetrieveUpdateDestroyAPIView,
)

app_name = 'employee_salary'

urlpatterns = [
    path('', Employee_Salary_ListCreateAPIView.as_view(), name = 'employee_salary_list_create'),
    path('<str:pk>/', Employee_Salary_RetrieveUpdateDestroyAPIView.as_view(), name = 'employee_salary_detail'),
]
