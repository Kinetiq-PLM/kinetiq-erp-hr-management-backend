from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EmployeePerformanceViewSerializer

class EmployeePerformanceViewList(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM employee_performance_view")
            rows = cursor.fetchall()

        data = [
            {
                "performance_id": row[0],
                "employee": row[1],
                "superior": row[2],
                "rating": row[3],
                "bonus_percentage": row[4],
                "bonus_amount": row[5],
                "review_date": row[6],
            }
            for row in rows
        ]
        serializer = EmployeePerformanceViewSerializer(data, many=True)
        return Response(serializer.data)
