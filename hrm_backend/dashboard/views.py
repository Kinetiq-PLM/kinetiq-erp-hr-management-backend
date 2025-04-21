from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from attendance_tracking.models import Attendance_Tracking
from employees.models import Employee
from employee_leave_requests.models import Employee_Leave_Request
from candidates.models import Candidate
from calendar_dates.models import Calendar_Date
from datetime import date

@api_view(['GET'])
def hr_dashboard_data(request):
    today = date.today()

    total_employees = Employee.objects.count()
    present_today = Attendance_Tracking.objects.filter(date=today, status = 'Present').count()
    absent_today = Attendance_Tracking.objects.filter(date=today, status = 'Absent').count()
    half_day = Attendance_Tracking.objects.filter(date=today, status = 'Half Day').count()
    on_leave = Employee_Leave_Request.objects.filter(start_date__lte = today, end_date__gte = today).count()

    interviews_today = Calendar_Date.objects.filter(date = today, type = 'Interview')
    candidates = Candidate.objects.order_by('-created_at')[:5]
    leave_requests = Employee_Leave_Request.objects.order_by('-created_at')[:5]

    data = {
        "employee_summary": {
            "total": total_employees,
            "present": present_today,
            "absent": absent_today,
            "half_day": half_day,
            "on_leave": on_leave,
        },
        "interviews_today": [
            {
                "title": interview.title,
                "time": interview.time.strftime('%H:%M') if interview.time else None
            } for interview in interviews_today
        ],
        "latest_candidates": [
            {
                "candidate_id": c.candidate_id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "applied": c.created_at
            } for c in candidates
        ],
        "recent_leave_requests": [
            {
                "employee_id": lr.employee.employee_id,
                "leave_id": lr.leave_id,
                "leave_type": lr.leave_type,
                "start": lr.start_date,
                "end": lr.end_date,
                "status": lr.status,
            } for lr in leave_requests
        ]
    }

    return Response(data)
