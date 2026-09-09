from django.db import models
from django.core.validators import MinValueValidator


class RoomType(models.Model):
    """
    Defines a category of room (e.g. Standard, Deluxe) and its two
    editable rates. Both rates and the short-time duration are plain
    fields — never hardcoded — so the Owner/GM can change them from
    the Django admin (or a future settings screen) at any time.
    """

    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(
        default=2, help_text="Max guests this room type sleeps."
    )
    night_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Full-night rate in ZMW (e.g. 450.00).",
    )
    short_time_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Short-time / day-use rate in ZMW (e.g. 200.00).",
    )
    short_time_hours = models.PositiveIntegerField(
        default=4,
        help_text="Number of hours covered by the short-time rate.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to retire this room type without deleting it "
        "(keeps historical bookings/rates intact).",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    """
    A single physical room. Rooms are never hard-deleted — see
    RoomAdmin in admin.py, which disables delete permission entirely
    and replaces it with an "archive" action that sets is_active=False.
    This keeps every past Reservation/Folio/Payment referencing this
    room fully intact.
    """

    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("dirty", "Dirty"),
        ("clean", "Clean"),
        ("maintenance", "Maintenance"),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,  # can't delete a RoomType while rooms use it
        related_name="rooms",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Archived (soft-deleted) rooms are hidden from booking "
        "but keep their history.",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["room_number"]

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.name})"
