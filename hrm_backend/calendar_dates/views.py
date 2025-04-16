from rest_framework import viewsets
from .models import Calendar_Date
from .serializers import (
    Calendar_Date_Serializer,
    Calendar_Date_CreateSerializer,
)

class CalendarDateViewSet(viewsets.ModelViewSet):
    queryset = Calendar_Date.objects.all()
    lookup_field = 'date'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Calendar_Date_CreateSerializer
        return Calendar_Date_Serializer
