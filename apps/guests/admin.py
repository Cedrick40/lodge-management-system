from django.contrib import admin
from .models import Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "nationality", "created_at")
    search_fields = ("full_name", "phone", "email")