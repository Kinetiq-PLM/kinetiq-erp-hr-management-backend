from django.urls import path
from . import views

app_name = 'department_superiors'

urlpatterns = [
    path('<str:pk>/archive/', views.archive_department_superior, name='department_superior_archive'),
    path('archived/', views.ArchivedDepartmentSuperiorListView.as_view(), name='archived_department_superiors'),
    path('<str:pk>/unarchive/', views.unarchive_department_superior, name='department_superior_unarchive'),
]
