from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Employee_Leave_Request_ViewSet

app_name = 'leave_requests'

router = DefaultRouter()
router.register(r'leave_requests', Employee_Leave_Request_ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
