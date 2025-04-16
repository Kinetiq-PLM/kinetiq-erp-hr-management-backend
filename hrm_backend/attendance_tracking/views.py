from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Attendance_Tracking
from calendar_dates.models import Calendar_Date
from .serializers import (
    Attendance_Tracking_Serializer,
    Attendance_Tracking_CreateSerializer,
    Barcode_Scan_Serializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from employees.models import Employee
from datetime import date

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('attendance.view_attendance'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Attendance_Tracking_CreateSerializer
        elif self.action == 'scan_barcode':
            return Barcode_Scan_Serializer
        return Attendance_Tracking_Serializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance_Tracking.objects.all()
    lookup_field = 'attendance_id'
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Attendance_Tracking_CreateSerializer
        elif self.action == 'scan_barcode':
            return Barcode_Scan_Serializer
        return Attendance_Tracking_Serializer

    def perform_create(self, serializer):
        today = date.today()
        if Calendar_Date.is_holiday(today):
            status = 'On Leave'
        else:
            status = 'Present'

    def perform_update(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)
        read_serializer = Attendance_Tracking_Serializer(serializer.instance, context = {'request': request})
        return Response(read_serializer.data, status = status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def scan_barcode(self, request):
        serializer = Barcode_Scan_Serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = serializer.validated_data['employee_id']
        
        employee = Employee.objects.filter(employee_id = employee_id).first()
        
        if not employee:
            return Response({"error": "Employee not found."}, status = status.HTTP_404_NOT_FOUND)
        
        today = date.today()

        calendar_date = Calendar_Date.objects.filter(date = today).first()
        if not calendar_date:
            return Response({"error": "No calendar data available for today."}, status = status.HTTP_400_BAD_REQUEST)

        attendance, created = Attendance_Tracking.objects.get_or_create(
            employee = employee,
            date = today,
            defaults={"calendar_date": calendar_date}
        )

        if created:
            return Response({"detail": "Attendance marked successfully."}, status = status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Attendance already marked for today."}, status = status.HTTP_200_OK)