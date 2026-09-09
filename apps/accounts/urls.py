from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("staff/", views.StaffListView.as_view(), name="staff_list"),
    path("staff/add/", views.StaffCreateView.as_view(), name="staff_add"),
    path("staff/<int:pk>/edit/", views.StaffUpdateView.as_view(), name="staff_edit"),
    path(
        "staff/<int:pk>/toggle-active/",
        views.StaffToggleActiveView.as_view(),
        name="staff_toggle_active",
    ),
    path(
        "staff/<int:pk>/reset-password/",
        views.StaffResetPasswordView.as_view(),
        name="staff_reset_password",
    ),
]