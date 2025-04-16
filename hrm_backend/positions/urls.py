from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PositionViewSet

# Initialize the router
router = DefaultRouter()
# Register the PositionViewSet with the router
router.register(r'positions', PositionViewSet)

app_name = 'positions'

urlpatterns = [
    # Include the default router URLs
    path('', include(router.urls)),
]