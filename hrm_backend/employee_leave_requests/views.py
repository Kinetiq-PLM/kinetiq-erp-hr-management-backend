from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import LeaveRequest
from .serializers import Employee_Leave_Request_HistorySerializer
from rest_framework.permissions import IsAuthenticated
class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('human_resources.view_leaverequest'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True
class Employee_Leave_Request_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    serializer_class = Employee_Leave_Request_HistorySerializer

    def get_queryset(self):
        return LeaveRequest.objects.filter(status__in=["Pending", "Approved", "Rejected"])
class Employee_Leave_Request_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = LeaveRequest.objects.all()
    serializer_class = Employee_Leave_Request_HistorySerializer
    lookup_field = 'leave_id'
class Employee_Leave_Request_ArchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, leave_id):
        leave = get_object_or_404(LeaveRequest, leave_id = leave_id)
        if leave.status == "Archived":
            return Response({"detail": "Leave request already archived."}, status = status.HTTP_400_BAD_REQUEST)
        leave.status = "Archived"
        leave.save()
        return Response({"detail": "Leave request archived successfully."}, status = status.HTTP_200_OK)
class Employee_Leave_Request_UnarchiveAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def post(self, request, leave_id):
        leave = get_object_or_404(LeaveRequest, leave_id = leave_id)
        if leave.status != "Archived":
            return Response({"detail": "Leave request is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        leave.status = "Pending"
        leave.save()
        return Response({"detail": "Leave request unarchived successfully."}, status = status.HTTP_200_OK)

class Employee_Leave_Request_ArchiveListAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    serializer_class = Employee_Leave_Request_HistorySerializer

    def get_queryset(self):
        return LeaveRequest.objects.filter(status = "Archived")

class Employee_Leave_Request_HistoryView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get(self, request, *args, **kwargs):
        leave_id = kwargs.get('leave_id')
        if leave_id:
            try:
                leave = LeaveRequest.objects.get(leave_id = leave_id)
                history = leave.history.all()  # django-simple-history
                serializer = Employee_Leave_Request_HistorySerializer(history, many = True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LeaveRequest.DoesNotExist:
                return Response({"detail": "Leave request not found."}, status = status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Leave ID is required."}, status = status.HTTP_400_BAD_REQUEST)
