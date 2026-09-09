from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path

from .forms import BulkRoomCreateForm
from .models import Room, RoomType


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "capacity",
        "night_rate",
        "short_time_rate",
        "short_time_hours",
        "is_active",
    )
    list_editable = ("night_rate", "short_time_rate", "short_time_hours", "is_active")
    search_fields = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "status", "is_active")
    list_editable = ("status", "is_active")
    list_filter = ("room_type", "status", "is_active")
    search_fields = ("room_number",)
    actions = ["archive_rooms"]

    # Points Django at our custom template that adds the
    # "Bulk Add Rooms" button next to the normal "Add room +" button.
    change_list_template = "admin/rooms/room/change_list.html"

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Archive selected rooms (soft-delete)")
    def archive_rooms(self, request, queryset):
        updated = queryset.update(is_active=False, status="maintenance")
        self.message_user(request, f"{updated} room(s) archived.")

    def get_urls(self):
        custom_urls = [
            path(
                "bulk-add/",
                self.admin_site.admin_view(self.bulk_add_view),
                name="rooms_room_bulk_add",
            ),
        ]
        return custom_urls + super().get_urls()

    def bulk_add_view(self, request):
        if request.method == "POST":
            form = BulkRoomCreateForm(request.POST)
            if form.is_valid():
                numbers = form.get_room_numbers()
                room_type = form.cleaned_data["room_type"]
                status = form.cleaned_data["default_status"]

                created_count = 0
                skipped = []
                for number in numbers:
                    _, was_created = Room.objects.get_or_create(
                        room_number=number,
                        defaults={"room_type": room_type, "status": status},
                    )
                    if was_created:
                        created_count += 1
                    else:
                        skipped.append(number)

                if created_count:
                    messages.success(request, f"{created_count} room(s) created.")
                if skipped:
                    messages.warning(
                        request,
                        f"Skipped {len(skipped)} room number(s) that already existed: "
                        f"{', '.join(skipped)}",
                    )
                return redirect("admin:rooms_room_changelist")
        else:
            form = BulkRoomCreateForm()

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "title": "Bulk Add Rooms",
            "opts": self.model._meta,
        }
        return render(request, "admin/rooms/room/bulk_add.html", context)