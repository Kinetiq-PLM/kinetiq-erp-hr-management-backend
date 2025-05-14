from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Onboarding
from .serializers import Onboarding_Serializer
from rest_framework.decorators import action

class Onboarding_ViewSet(viewsets.ModelViewSet):
    queryset = Onboarding.objects.all()
    serializer_class = Onboarding_Serializer
    lookup_field = 'onboarding_id'

    def get_queryset(self):
        try:
            return Onboarding.objects.filter(is_archived=False)
        except Exception as e:
            # Log the exception
            print(f"Error retrieving onboarding records: {str(e)}")
            return Onboarding.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve onboarding records: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Onboarding.DoesNotExist:
            return Response(
                {"error": "Onboarding record not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve onboarding record: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, onboarding_id=None):
        try:
            instance = self.get_object()
            instance.is_archived = True
            instance.save()
            return Response({'detail': 'Onboarding record archived.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to archive onboarding record: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='unarchive')
    def unarchive(self, request, onboarding_id=None):
        try:
            instance = self.get_object()
            instance.is_archived = False
            instance.save()
            return Response({'detail': 'Onboarding record unarchived.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to unarchive onboarding record: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
