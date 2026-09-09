from django.shortcuts import render
from django.views import View
from apps.accounts.permissions import permission_required, RolePermissionMixin

# --- Class-based view example ---
# Only the Owner/GM can archive rooms or edit room types/rates.

class RoomSettingsView(RolePermissionMixin, View):
    permission_module = "room_staff_mgmt"
    permission_action = "full"

    def get(self, request):
        # ... render the room/room-type management screen
        return render(request, "rooms/settings.html")