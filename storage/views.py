from django.db.models import Q
from django.http import FileResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Folder, File, FolderPermission, FilePermission
from .serializers import FolderSerializer, FileSerializer, ShareSerializer
from .services import get_folder_access, get_file_access
from accounts.models import User
from activity_logs.services import create_log

class RootDriveView(APIView):
    def get(self, request):

        search = request.GET.get("search")
        starred = request.GET.get("starred")

        sort = request.GET.get("sort", "name")
        order = request.GET.get("order", "asc")

        owned = request.GET.get("owned")

        folders = Folder.objects.filter(
            Q(owner=request.user) |
            Q(folderpermission__user=request.user),
            parent=None
        )

        files = File.objects.filter(
            Q(owner=request.user) |
            Q(filepermission__user=request.user),
            folder=None
        )

        # OWNED FILTER
        if owned is not None:

            is_owned = owned.lower() == "true"

            if is_owned:
                folders = folders.filter(owner=request.user)
                files = files.filter(owner=request.user)

            else:
                folders = folders.exclude(owner=request.user)
                files = files.exclude(owner=request.user)

        # SEARCH
        if search:
            folders = folders.filter(name__icontains=search)
            files = files.filter(name__icontains=search)

        # STAR FILTER
        if starred is not None:

            is_starred = starred.lower() == "true"

            folders = folders.filter(is_starred=is_starred)
            files = files.filter(is_starred=is_starred)

        # SORT
        allowed_sort_fields = {
            "name": "name",
            "owner": "owner__username",
            "starred": "is_starred",
        }

        sort_field = allowed_sort_fields.get(sort, "name")

        if order == "desc":
            sort_field = f"-{sort_field}"

        folders = folders.order_by(sort_field).distinct()
        files = files.order_by(sort_field).distinct()

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
            return Response(
                {"detail": "Forbidden"},
                status=403
            )

        search = request.GET.get("search")
        starred = request.GET.get("starred")

        sort = request.GET.get("sort", "name")
        order = request.GET.get("order", "asc")

        owned = request.GET.get("owned")

        folders = folder.folder_set.all()
        files = folder.file_set.all()

        # OWNED FILTER
        if owned is not None:

            is_owned = owned.lower() == "true"

            if is_owned:
                folders = folders.filter(owner=request.user)
                files = files.filter(owner=request.user)

            else:
                folders = folders.exclude(owner=request.user)
                files = files.exclude(owner=request.user)

        # SEARCH
        if search:
            folders = folders.filter(name__icontains=search)
            files = files.filter(name__icontains=search)

        # STAR FILTER
        if starred is not None:

            is_starred = starred.lower() == "true"

            folders = folders.filter(is_starred=is_starred)
            files = files.filter(is_starred=is_starred)

        # SORT
        allowed_sort_fields = {
            "name": "name",
            "owner": "owner__username",
            "starred": "is_starred",
        }

        sort_field = allowed_sort_fields.get(sort, "name")

        if order == "desc":
            sort_field = f"-{sort_field}"

        folders = folders.order_by(sort_field)
        files = files.order_by(sort_field)

        create_log(
            request.user,
            "VIEW_FOLDER",
            "FOLDER",
            folder.id,
            folder.name
        )

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

        user_ids = set(serializer.validated_data["user_ids"])
        user_access_levels = serializer.validated_data["user_access_levels"]

        if len(user_ids) > 0:
            users = User.objects.filter(id__in=user_ids)
            user_map = {u.id: u for u in users}

            # 1. create/update
            for user_id, access_level in zip(user_ids, user_access_levels):

                user = user_map.get(user_id)
                if not user:
                    continue

                FolderPermission.objects.update_or_create(
                    user=user,
                    folder=folder,
                    defaults={
                        "access_level": access_level,
                        "shared_by": request.user
                    }
                )

        # 2. DELETE missing users (IMPORTANT PART)
        FolderPermission.objects.filter(
            folder=folder
        ).exclude(
            user_id__in=user_ids
        ).delete()

        return Response({
            "detail": "Permission Updated"
        })

class FileShareView(APIView):
    def post(self, request, pk):

        file_obj = File.objects.get(pk=pk)

        serializer = ShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = set(serializer.validated_data["user_ids"])
        user_access_levels = serializer.validated_data["user_access_levels"]

        if len(user_ids) > 0:
            users = User.objects.filter(id__in=user_ids)
            user_map = {u.id: u for u in users}

            # 1. ADD / UPDATE permissions
            for user_id, access_level in zip(user_ids, user_access_levels):

                user = user_map.get(user_id)
                if not user:
                    continue

                FilePermission.objects.update_or_create(
                    user=user,
                    file=file_obj,
                    defaults={
                        "access_level": access_level,
                        "shared_by": request.user
                    }
                )

        # 2. DELETE removed users (SYNC STEP)
        FilePermission.objects.filter(
            file=file_obj
        ).exclude(
            user_id__in=user_ids
        ).delete()

        create_log(
            request.user,
            "SHARE_FILE",
            "FILE",
            file_obj.id,
            file_obj.name
        )

        return Response({
            "detail": "Permission Updated"
        })

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


class FolderMyPermissionView(APIView):
    def get(self, request, pk):

        folder = Folder.objects.get(pk=pk)

        permission = FolderPermission.objects.filter(
            folder=folder,
            user=request.user
        ).first()

        return Response({
            "has_access": permission is not None,
            "access_level": permission.access_level if permission else None
        })

class FileMyPermissionView(APIView):
    def get(self, request, pk):

        file_obj = File.objects.get(pk=pk)

        permission = FilePermission.objects.filter(
            file=file_obj,
            user=request.user
        ).first()

        return Response({
            "has_access": permission is not None,
            "access_level": permission.access_level if permission else None
        })


class FolderPermissionUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        folder = Folder.objects.get(pk=pk)

        access, _ = get_folder_access(request.user, folder)

        if not access:
            return Response(
                {"detail": "Forbidden"},
                status=403
            )

        users = User.objects.exclude(id=request.user.id)

        permissions = FolderPermission.objects.filter(
            folder=folder
        )

        permission_map = {
            p.user_id: p.access_level
            for p in permissions
        }

        data = []

        for user in users:
            data.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "has_access": user.id in permission_map,
                "access_level": permission_map.get(user.id)
            })

        return Response(data)

class FilePermissionUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        file_obj = File.objects.get(pk=pk)

        access, _ = get_file_access(request.user, file_obj)

        if not access:
            return Response(
                {"detail": "Forbidden"},
                status=403
            )

        users = User.objects.exclude(id=request.user.id)

        permissions = FilePermission.objects.filter(
            file=file_obj
        )

        permission_map = {
            p.user_id: p.access_level
            for p in permissions
        }

        data = []

        for user in users:
            data.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "has_access": user.id in permission_map,
                "access_level": permission_map.get(user.id)
            })

        return Response(data)