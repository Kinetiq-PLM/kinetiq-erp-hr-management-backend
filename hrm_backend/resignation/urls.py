from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResignationViewSet

router = DefaultRouter()
router.register(r'', ResignationViewSet)

app_name = 'resignation'

urlpatterns = [
    path('', include(router.urls)),
]