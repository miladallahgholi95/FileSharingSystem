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
            "owned": obj.owner == user,
            "access_level": access,
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
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    user_access_levels = serializers.ListField(
        child=serializers.ChoiceField(choices=["VIEW", "EDIT"]),
        allow_empty=False
    )

    def validate(self, attrs):
        user_ids = attrs.get("user_ids")
        user_access_levels = attrs.get("user_access_levels")

        if not user_access_levels:
            attrs["user_access_levels"] = ["VIEW"] * len(user_ids)
            return attrs

        if len(user_ids) != len(user_access_levels):
            raise serializers.ValidationError(
                "user_ids and user_access_levels must have same length"
            )

        return attrs