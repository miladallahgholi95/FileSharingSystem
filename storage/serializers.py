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
            "is_owned": obj.owner == user,
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
            "is_owned": obj.owner == user,
            "access_level": access,
        }

class ShareSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True
    )

    user_access_levels = serializers.ListField(
        child=serializers.ChoiceField(choices=["VIEW", "EDIT"]),
        required=False,
        allow_empty=True
    )

    def validate(self, attrs):

        user_ids = attrs.get("user_ids", [])

        user_access_levels = attrs.get("user_access_levels",[])

        if not user_access_levels:
            attrs["user_access_levels"] = ["VIEW"] * len(user_ids)
            return attrs

        if len(user_access_levels) < len(user_ids):
            remain_count = len(user_ids) - len(user_access_levels)

            user_access_levels.extend(["VIEW"] * remain_count)

        elif len(user_access_levels) > len(user_ids):
            raise serializers.ValidationError(
                "user_access_levels length cannot be greater than user_ids length"
            )

        attrs["user_access_levels"] = user_access_levels

        return attrs