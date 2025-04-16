from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Employee_Leave_BalanceViewSet

app_name = 'employee_leave_balances'

router = DefaultRouter()
router.register(r'employee_leave_balances', Employee_Leave_BalanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
