from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Interview
from .serializers import Interview_Serializer
from django.utils import timezone
from rest_framework import status

class Interview_ViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = Interview_Serializer
    lookup_field = 'interview_id'

    def get_queryset(self):
        return Interview.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail = True, methods = ['post'], url_path = 'approve')
    def approve(self, request, interview_id=None):
        instance = self.get_object()
        if instance.status == 'Approved':
            return Response({"detail": "Already approved."}, status = status.HTTP_400_BAD_REQUEST)
        instance.status = 'Approved'
        instance.updated_at = timezone.now()
        instance.save()
        return Response({"detail": "Interview request approved."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'], url_path = 'reject')
    def reject(self, request, interview_id=None):
        instance = self.get_object()
        if instance.status == 'Rejected':
            return Response({"detail": "Already rejected."}, status = status.HTTP_400_BAD_REQUEST)
        instance.status = 'Rejected'
        instance.updated_at = timezone.now()
        instance.save()
        return Response({"detail": "Interview request rejected."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'], url_path = 'archive')
    def archive(self, request, interview_id=None):
        instance = self.get_object()
        if instance.is_archived:
            return Response({"detail": "Already archived."}, status = status.HTTP_400_BAD_REQUEST)
        instance.is_archived = True
        instance.updated_at = timezone.now()
        instance.save()
        return Response({"detail": "Interview archived."}, status = status.HTTP_200_OK)
