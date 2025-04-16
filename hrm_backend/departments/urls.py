from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet

router = DefaultRouter()
router.register(r'department', DepartmentViewSet, basename = 'department')

app_name = 'departments'

urlpatterns = [
    path('', include(router.urls)),
]
