from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('<str:pk>/archive/', views.archive_employee, name='employee_archive'),
    path('archived/', views.ArchivedEmployeeListView.as_view(), name='archived_employees'),
    path('<str:pk>/unarchive/', views.unarchive_employee, name='employee_unarchive'),
]
