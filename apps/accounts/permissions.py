"""
Role-based permission checks, decorators, and mixins.

ROLE_PERMISSIONS below is a direct translation of the Section 5 role
matrix from the master prompt. Every module/action pair maps to the
exact set of roles allowed to do it — if you need to change who can
do what, change it HERE, not inside individual views.
"""

from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

OWNER_GM = "OWNER_GM"
FRONT_DESK = "FRONT_DESK"
HOUSEKEEPING = "HOUSEKEEPING"
BAR_STAFF = "BAR_STAFF"
ACCOUNTANT = "ACCOUNTANT"

# module -> action -> {roles allowed to perform that action}
ROLE_PERMISSIONS = {
    "reservations": {
        "view": {OWNER_GM, FRONT_DESK, ACCOUNTANT},
        "create_edit": {OWNER_GM, FRONT_DESK},
        "full": {OWNER_GM},
    },
    "front_desk": {
        "room_status": {OWNER_GM, FRONT_DESK, HOUSEKEEPING},  # Housekeeping: status only
        "full": {OWNER_GM, FRONT_DESK},
    },
    "billing": {
        "post_charges": {OWNER_GM, FRONT_DESK, BAR_STAFF},
        "view": {OWNER_GM, FRONT_DESK, ACCOUNTANT},
        "full": {OWNER_GM, ACCOUNTANT},
    },
    "reports": {
        "basic": {OWNER_GM, FRONT_DESK},
        "full": {OWNER_GM, ACCOUNTANT},
    },
    "room_staff_mgmt": {
        "full": {OWNER_GM},
    },
    "settings": {
        "full": {OWNER_GM},
    },
}


def has_permission(user, module, action):
    """
    True if `user`'s role is allowed to perform `action` in `module`,
    per ROLE_PERMISSIONS above. Superusers always pass (for the Django
    admin / initial setup account).
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    allowed_roles = ROLE_PERMISSIONS.get(module, {}).get(action, set())
    return getattr(user, "role", None) in allowed_roles


def permission_required(module, action):
    """
    Decorator for function-based views.

    Usage:
        @permission_required("billing", "post_charges")
        def bar_pos_charge_to_room(request, ...):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, module, action):
                raise PermissionDenied(
                    f"Your role does not have '{action}' access to '{module}'."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


class RolePermissionMixin(AccessMixin):
    """
    Mixin for class-based views.

    Usage:
        class BarPOSChargeView(RolePermissionMixin, View):
            permission_module = "billing"
            permission_action = "post_charges"
            ...
    """

    permission_module = None
    permission_action = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not has_permission(request.user, self.permission_module, self.permission_action):
            raise PermissionDenied(
                f"Your role does not have '{self.permission_action}' "
                f"access to '{self.permission_module}'."
            )
        return super().dispatch(request, *args, **kwargs)