from django.db.models import Q
from django.http import FileResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Folder, File, FolderPermission, FilePermission
from .serializers import FolderSerializer, FileSerializer, ShareSerializer
from .services import get_folder_access, get_file_access
from accounts.models import User
from activity_logs.services import create_log

class RootDriveView(APIView):
    def get(self, request):
        search = request.GET.get("search")

        folders = Folder.objects.filter(
            Q(owner=request.user) | Q(folderpermission__user=request.user),
            parent=None
        )

        files = File.objects.filter(
            Q(owner=request.user) | Q(filepermission__user=request.user),
            folder=None
        )

        if search:
            folders = folders.filter(name__icontains=search)
            files = files.filter(name__icontains=search)

        folders = folders.distinct()
        files = files.distinct()

        return Response({
            "folders": FolderSerializer(
                folders,
                many=True,
                context={"request": request}
            ).data,

            "files": FileSerializer(
                files,
                many=True,
                context={"request": request}
            ).data,
        })

class FolderContentView(APIView):
    def get(self, request, pk):
        folder = Folder.objects.get(pk=pk)

        access, _ = get_folder_access(request.user, folder)
        if not access:
            return Response({"detail":"Forbidden"}, status=403)

        search = request.GET.get("search")

        folders = folder.folder_set.all()
        files = folder.file_set.all()

        if search:
            folders = folders.filter(name__icontains=search)
            files = files.filter(name__icontains=search)

        create_log(request.user, "VIEW_FOLDER", "FOLDER", folder.id, folder.name)

        return Response({
            "folders": FolderSerializer(
                folders,
                many=True,
                context={"request":request}
            ).data,

            "files": FileSerializer(
                files,
                many=True,
                context={"request":request}
            ).data,
        })

class FolderCreateView(generics.CreateAPIView):
    serializer_class = FolderSerializer

    def perform_create(self, serializer):
        folder = serializer.save(owner=self.request.user, created_by=self.request.user)
        create_log(self.request.user, "CREATE_FOLDER", "FOLDER", folder.id, folder.name)

class FolderUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

class FileCreateView(generics.CreateAPIView):
    serializer_class = FileSerializer

    def perform_create(self, serializer):
        file_obj = serializer.save(owner=self.request.user, created_by=self.request.user)
        create_log(self.request.user, "UPLOAD_FILE", "FILE", file_obj.id, file_obj.name)

class FileUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer

class FileDownloadView(APIView):
    def get(self, request, pk):
        file_obj = File.objects.get(pk=pk)
        access, _ = get_file_access(request.user, file_obj)
        if not access:
            return Response(status=403)

        create_log(request.user, "DOWNLOAD_FILE", "FILE", file_obj.id, file_obj.name)
        return FileResponse(file_obj.file.open(), as_attachment=True)

class FolderShareView(APIView):
    def post(self, request, pk):
        folder = Folder.objects.get(pk=pk)
        serializer = ShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        permission, _ = FolderPermission.objects.update_or_create(
            user=User.objects.get(pk=serializer.validated_data["user_id"]),
            folder=folder,
            defaults={
                "access_level": serializer.validated_data["access_level"],
                "shared_by": request.user
            }
        )

        create_log(request.user, "SHARE_FOLDER", "FOLDER", folder.id, folder.name)
        return Response({"detail":"Shared"})

class FileShareView(APIView):
    def post(self, request, pk):
        file_obj = File.objects.get(pk=pk)
        serializer = ShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        FilePermission.objects.update_or_create(
            user=User.objects.get(pk=serializer.validated_data["user_id"]),
            file=file_obj,
            defaults={
                "access_level": serializer.validated_data["access_level"],
                "shared_by": request.user
            }
        )

        create_log(request.user, "SHARE_FILE", "FILE", file_obj.id, file_obj.name)
        return Response({"detail":"Shared"})


class FolderStarView(APIView):
    def post(self, request, pk):
        folder = Folder.objects.get(pk=pk)

        access, _ = get_folder_access(request.user, folder)
        if not access:
            return Response({"detail": "Forbidden"}, status=403)

        folder.is_starred = not folder.is_starred
        folder.save()

        return Response({
            "detail": "Folder star updated",
            "is_starred": folder.is_starred
        })


class FileStarView(APIView):
    def post(self, request, pk):
        file_obj = File.objects.get(pk=pk)

        access, _ = get_file_access(request.user, file_obj)
        if not access:
            return Response({"detail": "Forbidden"}, status=403)

        file_obj.is_starred = not file_obj.is_starred
        file_obj.save()

        return Response({
            "detail": "File star updated",
            "is_starred": file_obj.is_starred
        })