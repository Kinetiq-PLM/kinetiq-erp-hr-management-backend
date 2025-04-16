from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Job_Posting_ViewSet

app_name = 'job_posting'

router = DefaultRouter()
router.register(r'job_postings', Job_Posting_ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
