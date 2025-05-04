from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Interview_ViewSet

router = DefaultRouter()
router.register(r'interviews', Interview_ViewSet, basename = 'interviews')

app_name = 'interviews'

urlpatterns = [
    path('', include(router.urls)),
]