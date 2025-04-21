from rest_framework import (
    viewsets,
    permissions
)
from rest_framework.exceptions import PermissionDenied
from .models import Employee_Leave_Balance
from .serializers import (
    Employee_Leave_Balance_Serializer,
    Employee_Leave_Balance_CreateSerializer,
)

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employee_leave_balances.view_employee_leave_balance'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Employee_Leave_BalanceViewSet(viewsets.ModelViewSet):
    queryset = Employee_Leave_Balance.objects.all()
    lookup_field = 'balance_id'
    # permission_classes = [permissions.IsAuthenticated, IsHRMember]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Employee_Leave_Balance_CreateSerializer
        return Employee_Leave_Balance_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
