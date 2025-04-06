from rest_framework import generics, status
from rest_framework.response import Response
from .models import DepartmentSuperior
from .serializers import DepartmentSuperiorSerializer

class DepartmentSuperiorListCreateAPIView(generics.ListCreateAPIView):
    queryset = DepartmentSuperior.objects.all()
    serializer_class = DepartmentSuperiorSerializer

class DepartmentSuperiorDestroyAPIView(generics.DestroyAPIView):
    queryset = DepartmentSuperior.objects.all()
    serializer_class = DepartmentSuperiorSerializer
    lookup_field = 'composite_key'

    def get_object(self):
        dept_id = self.kwargs['dept_id']
        superior_job_title = self.kwargs['superior_job_title']
        return DepartmentSuperior.objects.get(dept_id=dept_id, superior_job_title=superior_job_title)
