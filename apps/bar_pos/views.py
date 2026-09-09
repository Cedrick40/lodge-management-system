from django.shortcuts import render

from django.views import View
from apps.accounts.permissions import permission_required, RolePermissionMixin

# --- Function-based view example ---
# Bar staff, front desk, and the owner/GM can post a bar charge to a room.
@permission_required("billing", "post_charges")
def bar_pos_charge_to_room(request):
    # ... look up the active folio, add a FolioItem, etc.
    return render(request, "bar_pos/charge_to_room.html")