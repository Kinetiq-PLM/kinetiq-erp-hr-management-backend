from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Interview
from .serializers import Interview_Serializer
from django.utils import timezone
import uuid
from django.db import transaction
from rest_framework.exceptions import ValidationError

class Interview_ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing interviews
    """
    queryset = Interview.objects.all().order_by('-interview_date')
    serializer_class = Interview_Serializer
    lookup_field = 'interview_id'

    def get_queryset(self):
        """
        Get queryset with optional filters
        """
        queryset = Interview.objects.all().order_by('-interview_date')
        
        # Add filtering options
        is_archived = self.request.query_params.get('is_archived', None)
        status_filter = self.request.query_params.get('status', None)
        candidate_id = self.request.query_params.get('candidate_id', None)
        job_id = self.request.query_params.get('job_id', None)
        interviewer_id = self.request.query_params.get('interviewer_id', None)
        
        if is_archived is not None:
            is_archived = is_archived.lower() == 'true'
            queryset = queryset.filter(is_archived=is_archived)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        if candidate_id:
            queryset = queryset.filter(candidate__candidate_id=candidate_id)
            
        if job_id:
            queryset = queryset.filter(job__job_id=job_id)
            
        if interviewer_id:
            queryset = queryset.filter(interviewer__employee_id=interviewer_id)
            
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Get a specific interview
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new interview
        """
        try:
            # Generate a unique ID if not provided
            if not request.data.get('interview_id'):
                request.data['interview_id'] = f"INTV-{uuid.uuid4().hex[:8].upper()}"
                
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update an existing interview
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, interview_id=None):
        """
        Approve an interview
        """
        try:
            instance = self.get_object()
            if instance.status == 'Approved':
                return Response({"detail": "Already approved."}, status=status.HTTP_400_BAD_REQUEST)
            instance.status = 'Approved'
            instance.updated_at = timezone.now()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, interview_id=None):
        """
        Reject an interview
        """
        try:
            instance = self.get_object()
            if instance.status == 'Rejected':
                return Response({"detail": "Already rejected."}, status=status.HTTP_400_BAD_REQUEST)
            instance.status = 'Rejected'
            instance.updated_at = timezone.now()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, interview_id=None):
        """
        Archive an interview
        """
        try:
            instance = self.get_object()
            if instance.is_archived:
                return Response({"detail": "Already archived."}, status=status.HTTP_400_BAD_REQUEST)
            instance.is_archived = True
            instance.updated_at = timezone.now()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'], url_path='unarchive')
    def unarchive(self, request, interview_id=None):
        """
        Unarchive an interview
        """
        try:
            instance = self.get_object()
            if not instance.is_archived:
                return Response({"detail": "Not archived."}, status=status.HTTP_400_BAD_REQUEST)
            instance.is_archived = False
            instance.updated_at = timezone.now()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
