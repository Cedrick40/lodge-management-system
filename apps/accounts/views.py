from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import StaffCreateForm, StaffUpdateForm
from .models import User
from .permissions import RolePermissionMixin


class StaffListView(RolePermissionMixin, ListView):
    permission_module = "room_staff_mgmt"
    permission_action = "full"
    model = User
    template_name = "accounts/staff_list.html"
    context_object_name = "staff"

    def get_queryset(self):
        # Owner/GM sees everyone, including deactivated accounts --
        # nothing is hidden, just clearly marked as inactive.
        return User.objects.all().order_by("is_active", "role", "username")


class StaffCreateView(RolePermissionMixin, CreateView):
    permission_module = "room_staff_mgmt"
    permission_action = "full"
    model = User
    form_class = StaffCreateForm
    template_name = "accounts/staff_form.html"
    success_url = reverse_lazy("accounts:staff_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Staff account '{self.object.username}' created.")
        return response


class StaffUpdateView(RolePermissionMixin, UpdateView):
    permission_module = "room_staff_mgmt"
    permission_action = "full"
    model = User
    form_class = StaffUpdateForm
    template_name = "accounts/staff_form.html"
    success_url = reverse_lazy("accounts:staff_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Staff account '{self.object.username}' updated.")
        return response


class StaffToggleActiveView(RolePermissionMixin, View):
    """
    Deactivate/reactivate -- never a hard delete. Same soft-delete
    principle as rooms: the account (and everything it ever did --
    bookings created, charges posted) stays in the audit trail.
    """

    permission_module = "room_staff_mgmt"
    permission_action = "full"

    def post(self, request, pk):
        staff = get_object_or_404(User, pk=pk)

        if staff == request.user:
            messages.error(request, "You cannot deactivate your own account.")
        else:
            staff.is_active = not staff.is_active
            staff.save(update_fields=["is_active"])
            action = "reactivated" if staff.is_active else "deactivated"
            messages.success(request, f"Staff account '{staff.username}' {action}.")

        return redirect("accounts:staff_list")


class StaffResetPasswordView(RolePermissionMixin, View):
    """
    Lets the Owner/GM set a new password directly, without email.
    This exists alongside the standard email-based "Forgot your
    password?" flow on the login page -- at a rural lodge, email
    delivery isn't something to depend on, so the Owner/GM having a
    direct override matters more here than it would in a city hotel.
    """

    permission_module = "room_staff_mgmt"
    permission_action = "full"

    def get(self, request, pk):
        staff = get_object_or_404(User, pk=pk)
        form = SetPasswordForm(staff)
        return render(
            request, "accounts/staff_reset_password.html", {"form": form, "staff": staff}
        )

    def post(self, request, pk):
        staff = get_object_or_404(User, pk=pk)
        form = SetPasswordForm(staff, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Password for '{staff.username}' has been reset.")
            return redirect("accounts:staff_list")
        return render(
            request, "accounts/staff_reset_password.html", {"form": form, "staff": staff}
        )