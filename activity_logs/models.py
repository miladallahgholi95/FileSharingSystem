from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.IntegerField(null=True, blank=True)
    target_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
