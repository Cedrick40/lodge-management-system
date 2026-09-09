from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Extends Django's built-in UserAdmin so `role` shows up on the same
    screen used to create/edit any staff account — no separate screen
    needed, and no risk of someone getting created without a role.
    """

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Lodge Role", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Lodge Role", {"fields": ("role",)}),
    )
    list_display = DjangoUserAdmin.list_display + ("role",)
    list_filter = DjangoUserAdmin.list_filter + ("role",)
