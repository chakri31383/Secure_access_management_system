# dashboard/utils.py
from .models import RolePermission

def user_has_permission(user, permission_name):
    """
    permission_name: 'can_view', 'can_edit', 'can_delete', 'can_chat'
    """
    if not user or user.org_id is None:
        return False
    if user.role == "OrgAdmin":
        return True
    try:
        rp = RolePermission.objects.get(name=user.role, org_id=user.org_id)
        return bool(getattr(rp, permission_name, False))
    except RolePermission.DoesNotExist:
        return False
