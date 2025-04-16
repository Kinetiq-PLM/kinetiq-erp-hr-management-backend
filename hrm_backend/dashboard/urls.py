from django.urls import path
from .views import hr_dashboard_data

app_name = 'dashboard'

urlpatterns = [
    path('', hr_dashboard_data),
]
