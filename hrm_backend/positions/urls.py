from django.urls import path
from . import views

app_name = 'positions'

urlpatterns = [
    path('<str:pk>/archive/', views.archive_positions, name='positions_archive'),  # archive logic
    path('<str:pk>/unarchive/', views.positions, name='positions_unarchive'),  # unarchive logic
    path('archived/', views.ArchivedPositionsListView.as_view(), name='archived_positions'),  # archived list
]
