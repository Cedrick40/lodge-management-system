from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    """
    Custom user model. Every staff account gets exactly one role,
    which drives what they can see and do — enforced via the
    permission decorators/mixins in permissions.py, not by anything
    hardcoded into individual views.
    """

    class Role(models.TextChoices):
        OWNER_GM = "OWNER_GM", "Owner / General Manager"
        FRONT_DESK = "FRONT_DESK", "Front Desk"
        HOUSEKEEPING = "HOUSEKEEPING", "Housekeeping"
        BAR_STAFF = "BAR_STAFF", "Bar Staff"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        help_text="Determines what this staff member can access in the system.",
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
