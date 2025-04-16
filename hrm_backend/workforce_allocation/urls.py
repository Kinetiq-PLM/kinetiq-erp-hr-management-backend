from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Workforce_AllocationViewSet

router = DefaultRouter()
router.register(r'workforce_allocations', Workforce_AllocationViewSet)

app_name = 'workforce_allocation'

urlpatterns = [
    path('', include(router.urls)),
]
