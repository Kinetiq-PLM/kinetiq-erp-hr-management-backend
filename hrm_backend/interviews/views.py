from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Interview
from .serializers import Interview_Serializer
from django.utils import timezone
import uuid
from django.db import transaction, connection
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
            queryset = queryset.filter(candidate_id=candidate_id)
            
        if job_id:
            queryset = queryset.filter(job_id=job_id)
            
        if interviewer_id:
            queryset = queryset.filter(interviewer_id=interviewer_id)
            
        return queryset
        
    def list(self, request, *args, **kwargs):
        """Override list to ensure we properly serialize foreign keys"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to ensure we properly serialize foreign keys"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def archive(self, request, interview_id=None):
        """Archive an interview"""
        interview = self.get_object()
        interview.is_archived = True
        interview.save()
        return Response({"status": "Interview archived"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, interview_id=None):
        """Unarchive an interview"""
        interview = self.get_object()
        interview.is_archived = False
        interview.save()
        return Response({"status": "Interview unarchived"}, status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs):
        """Create a new interview with proper error handling"""
        try:
            with transaction.atomic():
                # Generate UUID if not provided
                if 'interview_id' not in request.data:
                    request.data['interview_id'] = f"INT-{timezone.now().year}-{uuid.uuid4().hex[:6]}"
                
                # Set created_at and updated_at
                request.data['created_at'] = timezone.now()
                request.data['updated_at'] = timezone.now()
                request.data['is_archived'] = False
                
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to create interview: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update an interview with proper error handling"""
        try:
            with transaction.atomic():
                # Set updated_at
                request.data['updated_at'] = timezone.now()
                
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                
                return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to update interview: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
