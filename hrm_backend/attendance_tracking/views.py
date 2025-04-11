from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import is_naive, make_aware, localtime
from employees.models import Employee
from .models import Attendance_Tracking
from .serializers import Attendance_Tracking_Serializer
from calendar_dates.models import Calendar_Date
# from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from uuid import uuid4


class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('attendance_tracking.view_attendance_tracking'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

# BARCODE API
class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('attendance_tracking.view_attendance_tracking'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True


class Barcode_ScanView(APIView):
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        weekday = today.weekday()
        is_weekend = weekday >= 5

        # Ensure today's calendar date exists
        Calendar_Date.objects.get_or_create(
            date=today,
            defaults={
                "is_workday": not is_weekend,
                "is_special": False,
                "is_holiday": False,
                "holiday_name": None,
                "holiday_type": None,
            }
        )

        attendance = Attendance_Tracking.objects.filter(employee=employee, date=today).first()

        if not attendance:
            attendance = Attendance_Tracking(
                employee=employee,
                date=today,
                time_in=timezone.now(),
                status="Present",
            )
            attendance.save()

        # Ensure datetimes are timezone-aware
        if is_naive(attendance.time_in):
            attendance.time_in = make_aware(attendance.time_in)

        if attendance.time_out and is_naive(attendance.time_out):
            attendance.time_out = make_aware(attendance.time_out)

        time_in_local = localtime(attendance.time_in)
        time_out_local = localtime(attendance.time_out) if attendance.time_out else None

        if request.query_params.get("action") == "clock_out":
            if attendance.time_out is None:
                attendance.time_out = timezone.now()
                attendance.status = "Clocked Out"
                attendance.save()
                return Response({
                    "message": "Clock-out successful",
                    "time_out": localtime(attendance.time_out),
                    "work_hours": (attendance.time_out - attendance.time_in).total_seconds() / 3600
                })

        return Response({
            "employee_id": employee.employee_id,
            "name": f"{employee.first_name} {employee.last_name}",
            "attendance_status": attendance.status,
            "time_in": time_in_local,
            "time_out": time_out_local,
            "work_hours": (
                (attendance.time_out - attendance.time_in).total_seconds() / 3600
                if attendance.time_out else None
            )
        })

class Attendance_Tracking_ViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Attendance_Tracking.objects.all()
    serializer_class = Attendance_Tracking_Serializer

    def get_queryset(self):
        return Attendance_Tracking.objects.filter(is_archived = False)

class Attendance_Tracking_ListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Attendance_Tracking.objects.all()
    serializer_class = Attendance_Tracking_Serializer

    def get_queryset(self):
        return Attendance_Tracking.objects.filter(is_archived = False)

class Attendance_Tracking_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Attendance_Tracking.objects.all()
    serializer_class = Attendance_Tracking_Serializer
    lookup_field = 'pk'

class Attendance_Tracking_DestroyAPIView(generics.DestroyAPIView):
    # permission_classes = [IsAuthenticated, IsHRMember]
    queryset = Attendance_Tracking.objects.all()
    serializer_class = Attendance_Tracking_Serializer
    lookup_field = 'attendance_id'
