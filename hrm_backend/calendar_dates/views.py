from rest_framework import generics
from .models import Calendar_Date
from .serializers import Calendar_Date_Serializer

class CalendarDate_ListCreateAPIView(generics.ListCreateAPIView):
    queryset = Calendar_Date.objects.all()
    serializer_class = Calendar_Date_Serializer

class CalendarDate_RetrieveAPIView(generics.RetrieveAPIView):
    queryset = Calendar_Date.objects.all()
    serializer_class = Calendar_Date_Serializer
    lookup_field = 'date'
