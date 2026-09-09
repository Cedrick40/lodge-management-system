from django import forms

from .models import Room, RoomType


class SingleRoomForm(forms.ModelForm):
    """
    Plain ModelForm — this is effectively what Django admin already
    uses for the normal "Add room" page. Kept here so single-add and
    bulk-add logic live together in one forms.py.
    """

    class Meta:
        model = Room
        fields = ["room_number", "room_type", "status", "notes"]


class BulkRoomCreateForm(forms.Form):
    """
    Creates many rooms in one submit — either a numeric range
    (e.g. 201 to 223) or a pasted custom list (e.g. "101, 101A, 102").
    Exactly one of the two must be provided, not both.
    """

    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.filter(is_active=True),
        help_text="All rooms created will use this room type.",
    )
    prefix = forms.CharField(
        max_length=10,
        required=False,
        help_text='Optional, added to every number, e.g. "R" -> R201, R202...',
    )
    range_start = forms.IntegerField(
        required=False,
        help_text="e.g. 201 (leave both range fields blank to use the custom list instead)",
    )
    range_end = forms.IntegerField(required=False, help_text="e.g. 223")
    custom_numbers = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Comma or newline separated, e.g. 101, 101A, 102 -- use this OR the range above, not both.",
    )
    default_status = forms.ChoiceField(choices=Room.STATUS_CHOICES, initial="available")

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("range_start"), cleaned.get("range_end")
        custom = cleaned.get("custom_numbers")

        has_range = start is not None and end is not None
        has_custom = bool(custom and custom.strip())

        if not has_range and not has_custom:
            raise forms.ValidationError(
                "Provide either a numeric range or a custom list of room numbers."
            )
        if has_range and has_custom:
            raise forms.ValidationError("Use the range OR the custom list, not both.")
        if has_range and start > end:
            raise forms.ValidationError("Range start must not be greater than range end.")

        return cleaned

    def get_room_numbers(self):
        """Returns the final list of room-number strings to create."""
        prefix = self.cleaned_data.get("prefix") or ""
        start = self.cleaned_data.get("range_start")
        end = self.cleaned_data.get("range_end")
        custom = self.cleaned_data.get("custom_numbers")

        if start is not None and end is not None:
            return [f"{prefix}{n}" for n in range(start, end + 1)]

        raw = custom.replace("\n", ",").split(",")
        return [f"{prefix}{n.strip()}" for n in raw if n.strip()]