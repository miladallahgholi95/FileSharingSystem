import os
from django.db import models
from django.conf import settings

ACCESS_CHOICES = [("VIEW","VIEW"),("EDIT","EDIT")]

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_folders")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_folders")
    description = models.TextField(blank=True)
    is_starred = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name","parent","owner")

class File(models.Model):
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_files")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_files")
    description = models.TextField(blank=True)
    is_starred = models.BooleanField(default=False)
    file = models.FileField(upload_to="uploads/")
    extension = models.CharField(max_length=20)
    size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name","folder","owner")

    def save(self, *args, **kwargs):
        if self.file:
            self.extension = os.path.splitext(self.file.name)[1]
            self.size = self.file.size
        super().save(*args, **kwargs)

class FolderPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=10, choices=ACCESS_CHOICES)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shared_folder_permissions")
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user","folder")

class FilePermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=10, choices=ACCESS_CHOICES)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shared_file_permissions")
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user","file")
