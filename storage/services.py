from .models import FolderPermission, FilePermission, Folder

def get_folder_access(user, folder):
    if folder.owner == user:
        return "EDIT", "OWNED"

    direct = FolderPermission.objects.filter(user=user, folder=folder).first()
    if direct:
        return direct.access_level, "DIRECT_SHARED"

    current = folder.parent
    while current:
        inherited = FolderPermission.objects.filter(user=user, folder=current).first()
        if inherited:
            return inherited.access_level, "INHERITED_SHARED"
        current = current.parent

    return None, None

def get_file_access(user, file_obj):
    if file_obj.owner == user:
        return "EDIT", "OWNED"

    direct = FilePermission.objects.filter(user=user, file=file_obj).first()
    if direct:
        return direct.access_level, "DIRECT_SHARED"

    if file_obj.folder:
        return get_folder_access(user, file_obj.folder)

    return None, None
