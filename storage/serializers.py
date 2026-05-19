from rest_framework import serializers
from .models import Folder, File, FolderPermission, FilePermission
from .services import get_folder_access, get_file_access

class FolderSerializer(serializers.ModelSerializer):
    visibility = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = "__all__"

    def get_visibility(self, obj):
        user = self.context["request"].user
        access, origin = get_folder_access(user, obj)
        return {
            "is_owned_by_current_user": obj.owner == user,
            "is_shared_with_current_user": origin is not None and origin != "OWNED",
            "access_origin": origin,
            "effective_access_level": access,
        }

class FileSerializer(serializers.ModelSerializer):
    visibility = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = "__all__"

    def get_visibility(self, obj):
        user = self.context["request"].user
        access, origin = get_file_access(user, obj)
        return {
            "is_owned_by_current_user": obj.owner == user,
            "is_shared_with_current_user": origin is not None and origin != "OWNED",
            "access_origin": origin,
            "effective_access_level": access,
        }

class ShareSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    access_level = serializers.ChoiceField(choices=["VIEW","EDIT"])
