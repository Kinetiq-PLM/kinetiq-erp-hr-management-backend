from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidateViewSet

app_name = 'candidates'

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
