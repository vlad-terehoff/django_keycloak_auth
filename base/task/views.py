from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = ['user', 'is_active', 'data_start', 'data_finish']
