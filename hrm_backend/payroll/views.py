from rest_framework import viewsets, permissions
from .models import Payroll
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .serializers import (
    Payroll_Serializer, 
    Payroll_CreateSerializer,
    Payroll_UpdateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all()
    lookup_field = 'payroll_id'
    # permission_classes = [IsAuthenticated, IsHRMember]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return Payroll_CreateSerializer
        elif self.action in ['update', 'partial_update']:
            return Payroll_UpdateSerializer
        return Payroll_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail = True, methods = ['post'])
    def finalize(self, request, pk = None):
        payroll = self.get_object()
        if payroll.status == 'Locked':
            return Response({"detail": "Payroll is already locked and cannot be edited."}, status = status.HTTP_400_BAD_REQUEST)
        payroll.status = 'Finalized'
        payroll.save()
        return Response({"detail": "Payroll finalized successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def lock(self, request, pk = None):
        payroll = self.get_object()
        if payroll.status == 'Locked':
            return Response({"detail": "Payroll is already locked."}, status = status.HTTP_400_BAD_REQUEST)
        payroll.status = 'Locked'
        payroll.save()
        return Response({"detail": "Payroll locked successfully."}, status = status.HTTP_200_OK)
