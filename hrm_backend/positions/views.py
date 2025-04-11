from rest_framework import generics
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.views import View
from rest_framework import viewsets, permissions
from .models import Position
from .serializers import PositionSerializer

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('positions.view_position')

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all().order_by('-created_at')
    serializer_class = PositionSerializer
    permission_classes = [IsHRMember]

# dont delete any here, this is for archiving and unarchiving
def archive_positions(request, pk):
    positions = get_object_or_404(Position, pk=pk)
    positions.is_archived = True
    positions.save()

    messages.success(request, f'Position "{positions.position_title}" archived successfully.')
    return redirect(reverse('admin:%s_%s_changelist' % (Position._meta.app_label, Position._meta.model_name)))

def positions(request, pk):
    positions = get_object_or_404(Position, pk=pk)
    positions.is_archived = False
    positions.save()

    messages.success(request, f'Position "{positions.position_title}" unarchived successfully.')
    return redirect(reverse('positions:archived_positions'))


# goes to the template archieved_positions.html 
class ArchivedPositionsListView(View):
    def get(self, request):
        archived_positions = Position.objects.filter(is_archived = True)
        context = {
            'archived_positions': archived_positions,
        }
        return render(request, 'admin/positions/archived_positions.html', context)
    permission_classes = [permissions.AllowAny]
