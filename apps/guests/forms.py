from django import forms
from .models import Guest

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ["full_name", "phone", "email", "nationality", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }