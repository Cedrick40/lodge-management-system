from django.urls import path
from . import views

app_name = "guests"

urlpatterns = [
    path("", views.guest_list, name="list"),
    path("new/", views.guest_create, name="create"),
    path("<int:pk>/", views.guest_detail, name="detail"),
    path("<int:pk>/edit/", views.guest_edit, name="edit"),
    path("search/", views.guest_search_api, name="search_api"),
]