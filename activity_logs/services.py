from .models import ActivityLog

def create_log(user, action, target_type, target_id, target_name):
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
        )
    except Exception:
        pass
