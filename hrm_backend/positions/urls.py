from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PositionViewSet

router = DefaultRouter()
router.register(r'positions', PositionViewSet)

app_name = 'positions'

urlpatterns = [
    path('', include(router.urls)),
    path('positions/<str:pk>/unarchive/', PositionViewSet.as_view({'post': 'unarchive'}), name = 'position-unarchive'),
]