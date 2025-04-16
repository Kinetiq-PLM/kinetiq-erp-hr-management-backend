from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Department_SuperiorViewSet

router = DefaultRouter()
router.register(r'department-superiors', Department_SuperiorViewSet)

app_name = 'department_superiors'

urlpatterns = [
    path('', include(router.urls)),
]
