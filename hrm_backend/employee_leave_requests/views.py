from rest_framework import (
    viewsets,
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Employee_Leave_Request
from .serializers import (
    Employee_Leave_Request_Serializer,
    Employee_Leave_Request_CreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import (
    PermissionDenied,
    APIException, 
    ValidationError,
)
from rest_framework.parsers import JSONParser
from django.db import IntegrityError
import re
import json

class LeaveBalanceException(APIException):
    status_code = 400
    default_detail = 'Insufficient leave balance'
    default_code = 'insufficient_balance'

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('human_resources.view_leaverequest'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class Employee_Leave_Request_ViewSet(viewsets.ModelViewSet):
    queryset = Employee_Leave_Request.objects.all()
    lookup_field = 'leave_id'
    parser_classes = [JSONParser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Employee_Leave_Request_CreateSerializer
        return Employee_Leave_Request_Serializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception = True)
            self.perform_create(serializer)
            return Response(
                self.get_serializer_class()(serializer.instance).data, 
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"detail": "Validation error", "errors": e.detail}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except LeaveBalanceException as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            error_message = str(e)
            
            if "Insufficient" in error_message or "leave cannot exceed" in error_message:
                match = re.search(r'DETAIL:\s*(.*?)(?:\n|$)', error_message)
                if match:
                    clean_message = match.group(1)
                else:
                    clean_message = error_message.replace('IntegrityError:', '').strip()
                
                raise LeaveBalanceException(detail=clean_message)
            else:
                raise APIException(detail=f"Error creating leave request: {error_message}")
        except Exception as e:
            print(f"Error creating leave request: {str(e)}")
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")

    def update(self, request, *args, **kwargs):
        """
        Override update method for better error handling
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data = request.data, partial = partial)
        
        try:
            serializer.is_valid(raise_exception = True)
            self.perform_update(serializer)
            return Response(
                self.get_serializer_class()(serializer.instance).data
            )
        except ValidationError as e:
            return Response(
                {"detail": "Validation error", "errors": e.detail}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_update(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            error_message = str(e)
            
            if "Insufficient" in error_message or "leave cannot exceed" in error_message:
                match = re.search(r'DETAIL:\s*(.*?)(?:\n|$)', error_message)
                if match:
                    clean_message = match.group(1)
                else:
                    clean_message = error_message.replace('IntegrityError:', '').strip()
                
                raise LeaveBalanceException(detail=clean_message)
            else:
                raise APIException(detail=f"Error updating leave request: {error_message}")
        except Exception as e:
            print(f"Error updating leave request: {str(e)}")
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")

    @action(detail = True, methods = ['post'])
    def archive(self, request, leave_id = None):
        leave = self.get_object()
        if leave.is_archived:
            return Response({"detail": "Leave request already archived."}, status = status.HTTP_400_BAD_REQUEST)
        
        leave.is_archived = True
        leave.save(update_fields = ['is_archived', 'updated_at'])
        return Response({"detail": "Leave request archived successfully."}, status = status.HTTP_200_OK)
    
    @action(detail = True, methods = ['post'])
    def unarchive(self, request, leave_id = None):
        leave = self.get_object()
        if not leave.is_archived:
            return Response({"detail": "Leave request is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        
        leave.is_archived = False
        leave.save(update_fields=['is_archived', 'updated_at'])
        return Response({"detail": "Leave request unarchived successfully."}, status = status.HTTP_200_OK)
    
    @action(detail = False, methods = ['get'])
    def archived(self, request):
        archived_leave_requests = Employee_Leave_Request.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_leave_requests, many = True)
        return Response(serializer.data)