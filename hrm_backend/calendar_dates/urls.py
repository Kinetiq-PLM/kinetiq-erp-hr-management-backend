from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CalendarDateViewSet

router = DefaultRouter()
router.register(r'calendar_dates', CalendarDateViewSet)

app_name = 'calendar_dates'

urlpatterns = [
    path('', include(router.urls)),
]
