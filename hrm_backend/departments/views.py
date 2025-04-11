from rest_framework import generics
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.views import View
from .models import Department
from .serializers import DepartmentSerializer
from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

class ArchivedDepartmentListAPIView(ListAPIView):
    queryset = Department.objects.filter(is_archived=True)
    serializer_class = DepartmentSerializer
class DepartmentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = 'pk'

class DepartmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated] # palitan to AllowAny if gustong magcreate

class DepartmentDestroyAPIView(generics.DestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = 'dept_id'
    permission_classes = [IsAuthenticated] # palitan to AllowAny if gustong magdelete

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

# archive logic (archiving and unarchiving)
def archive_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.is_archived = True
    department.save()

    messages.success(request, f'Department "{department.dept_name}" archived successfully.')
    return redirect(reverse('admin:%s_%s_changelist' % (Department._meta.app_label, Department._meta.model_name)))

def unarchive_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.is_archived = False
    department.save()

    messages.success(request, f'Department "{department.dept_name}" unarchived successfully.')
    return redirect(reverse('departments:archived_departments'))

# goes to the template archieved_departments.html 
class ArchivedDepartmentListView(View):
    def get(self, request):
        archived_departments = Department.objects.filter(is_archived = True)
        context = {
            'archived_departments': archived_departments,
        }
        return render(request, 'admin/departments/archived_departments.html', context)
