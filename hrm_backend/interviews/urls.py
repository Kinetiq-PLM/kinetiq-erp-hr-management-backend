from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Interview_ViewSet

# Create a router
router = DefaultRouter()

# Register the Interview_ViewSet with an empty prefix
# The actual path 'interviews/' is handled in the main urls.py
router.register('', Interview_ViewSet, basename='interviews')

app_name = 'interviews'

urlpatterns = [
    path('', include(router.urls)),
]