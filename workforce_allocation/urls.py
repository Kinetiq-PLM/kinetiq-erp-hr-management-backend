from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkforceAllocationViewSet

router = DefaultRouter()
router.register(r'workforce-allocation', WorkforceAllocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
