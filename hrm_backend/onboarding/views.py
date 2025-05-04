from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Onboarding
from .serializers import Onboarding_Serializer
from rest_framework.decorators import action

class Onboarding_ViewSet(viewsets.ModelViewSet):
    queryset = Onboarding.objects.all()
    serializer_class = Onboarding_Serializer
    lookup_field = 'onboarding_id'

    def get_queryset(self):
        return Onboarding.objects.filter(is_archived = False)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail = True, methods = ['post'], url_path = 'archive')
    def archive(self, request, onboarding_id = None):
        instance = self.get_object()
        instance.is_archived = True
        instance.save()
        return Response({'detail': 'Onboarding record archived.'}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'], url_path = 'unarchive')
    def unarchive(self, request, onboarding_id = None):
        instance = self.get_object()
        instance.is_archived = False
        instance.save()
        return Response({'detail': 'Onboarding record unarchived.'}, status = status.HTTP_200_OK)
