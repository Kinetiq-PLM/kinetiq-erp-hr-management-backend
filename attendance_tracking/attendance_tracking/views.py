from django.shortcuts import render
from django.views.generic import View
from attendance_tracking.mixins import AttendanceGroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
import uuid
import datetime
from employees.models import Employee
from .models import Attendance_Tracking
from .serializers import Attendance_Tracking_Serializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



#  Attendance View (HTML + QR POST)

class AttendanceScanView(LoginRequiredMixin, AttendanceGroupRequiredMixin, View):
    queryset = Attendance_Tracking.objects.all()
    serializer_class = Attendance_Tracking_Serializer

    def get(self, request):
        return render(request, 'attendance/attendance.html')

    def post(self, request):
        try:
            decoded_qr_text = request.POST.get('text')

            if not decoded_qr_text:
                return JsonResponse({'success': False, 'message': 'No QR code found'}, status=400)

            try:
                employee = Employee.objects.get(employee_id=decoded_qr_text)
            except Employee.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Employee not found'}, status=400)

            now = timezone.now()
            today = now.date()

            attendance_today = Attendance_Tracking.objects.filter(
                employee=employee,
                date=today
            ).order_by('-created_at').first()

            if not attendance_today:
                today_str = today.strftime("%Y%m%d")
                random_str = uuid.uuid4().hex[:5]
                attendance_id = f"HR-ATT-{today_str}-{random_str}"

                Attendance_Tracking.objects.create(
                    attendance_id=attendance_id,
                    employee=employee,
                    date=today,
                    time_in=now,
                    status="Present"
                )
                message = 'Check-in recorded successfully'

            elif attendance_today.status == "Present" and not attendance_today.time_out:
                attendance_today.time_out = now
                attendance_today.status = "Clocked Out"
                attendance_today.save()
                message = 'Check-out recorded successfully'

            elif attendance_today.status == "Clocked Out":
                message = 'You have already checked out today'
                return JsonResponse({'success': False, 'message': message}, status=200)

            return JsonResponse({
                'success': True,
                'message': message,
                'redirect_url': f"{reverse('attendance_tracking:attendance_marked')}?message={message}"
            }, status=200)

        except Exception as e:
            print("❌ Internal Server Error in AttendanceScanView POST:", str(e))
            return JsonResponse({'success': False, 'message': 'Internal server error'}, status=500)

class CustomLoginView(LoginView):
    template_name = 'attendance/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Login failed. Please check your credentials.")
        return super().form_invalid(form)


class AttendanceMarkedView(LoginRequiredMixin, AttendanceGroupRequiredMixin, View):
    def get(self, request):
        message = request.GET.get('message', 'Attendance Marked Successfully!')
        return render(request, 'attendance/attendance_marked.html', {'message': message})


# Attendance API ViewSet
class AttendanceTrackingViewSet(viewsets.ModelViewSet):
    queryset = Attendance_Tracking.objects.all().order_by('-created_at')
    serializer_class = Attendance_Tracking_Serializer
    lookup_field = 'attendance_id'

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        today = timezone.now().date()
        records = Attendance_Tracking.objects.filter(date=today)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, attendance_id=None):
        record = self.get_object()
        if record.status == 'Archived':
            return Response({"detail": "Already archived."}, status=status.HTTP_400_BAD_REQUEST)
        record.status = 'Archived'
        record.save()
        return Response({"detail": "Archived successfully."}, status=status.HTTP_200_OK)
