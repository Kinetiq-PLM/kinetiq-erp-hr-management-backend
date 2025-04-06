from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('<str:pk>/archive/', views.archive_department, name='department_archive'),
    path('archived/', views.ArchivedDepartmentListView.as_view(), name='archived_departments'),  # archived list
    path('<str:pk>/unarchive/', views.unarchive_department, name='department_unarchive'),  # unarchive logic
]
