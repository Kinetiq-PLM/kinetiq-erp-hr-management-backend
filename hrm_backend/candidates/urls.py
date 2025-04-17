from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Candidate_ViewSet

app_name = 'candidates'

router = DefaultRouter()
router.register(r'candidates', Candidate_ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
