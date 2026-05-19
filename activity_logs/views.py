from rest_framework import generics
from .models import ActivityLog
from .serializers import ActivityLogSerializer

class ActivityLogListView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return ActivityLog.objects.all().order_by("-created_at")
        return ActivityLog.objects.filter(user=self.request.user).order_by("-created_at")
