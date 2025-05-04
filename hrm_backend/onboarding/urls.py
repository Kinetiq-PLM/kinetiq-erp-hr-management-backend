from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Onboarding_ViewSet

app_name = 'onboarding'

router = DefaultRouter()
router.register(r'', Onboarding_ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
