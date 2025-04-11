from django.urls import path
from .views import Calendar_Date_ListCreateAPIView, Calendar_Date_RetrieveAPIView

app_name = 'calendar_dates'

urlpatterns = [
    path('', Calendar_Date_ListCreateAPIView.as_view(), name='calendar_date_list_create'),
    path('<str:date>/', Calendar_Date_RetrieveAPIView.as_view(), name='calendar_date_detail'),
]
