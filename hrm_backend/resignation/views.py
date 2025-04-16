from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Resignation
from .serializers import (
    ResignationSerializer,
    ResignationCreateSerializer,
    ResignationUpdateSerializer,
)
from rest_framework.permissions import IsAuthenticated


class ResignationViewSet(viewsets.ModelViewSet):
    queryset = Resignation.objects.all()
    lookup_field = 'resignation_id'
    # permission_classes = [IsAuthenticated, IsHRMember]


    def get_serializer_class(self):
        if self.action == 'create':
            return ResignationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ResignationUpdateSerializer
        return ResignationSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()