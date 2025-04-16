from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Job_Posting
from .serializers import (
    Job_Posting_Serializer,
    Job_Posting_CreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('job_postings.view_job_posting'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Job_Posting_ViewSet(viewsets.ModelViewSet):
    queryset = Job_Posting.objects.all()
    lookup_field = 'job_id'
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Job_Posting_CreateSerializer
        return Job_Posting_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail = True, methods = ['post'])
    def archive(self, request, pk = None):
        job_posting = self.get_object()
        if job_posting.is_archived:
            return Response({"detail": "Job posting already archived."}, status = status.HTTP_400_BAD_REQUEST)
        job_posting.is_archived = True
        job_posting.save()
        return Response({"detail": "Job posting archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, pk = None):
        job_posting = self.get_object()
        if not job_posting.is_archived:
            return Response({"detail": "Job posting is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        job_posting.is_archived = False
        job_posting.save()
        return Response({"detail": "Job posting unarchived successfully."}, status = status.HTTP_200_OK)

    @action(detail = False, methods = ['get'])
    def archived(self, request):
        archived_job_postings = Job_Posting.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_job_postings, many = True)
        return Response(serializer.data)