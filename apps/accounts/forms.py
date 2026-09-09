from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User


class StaffCreateForm(UserCreationForm):
    """
    Reuses Django's own UserCreationForm so password handling
    (hashing, confirmation matching, strength validation) is exactly
    Django's battle-tested logic -- we're only adding the fields the
    Owner/GM actually needs to set when onboarding someone.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "role"]


class StaffUpdateForm(forms.ModelForm):
    """
    Editing never touches the password -- if a password reset is
    needed, that's the separate flow being added in Module 1d, not
    something bundled into a general "edit details" form.
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "role", "is_active"]