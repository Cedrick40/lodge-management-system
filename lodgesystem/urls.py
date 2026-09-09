"""
URL configuration for lodgesystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    # Dashboard is the site's home page
    path("", include("apps.dashboard.urls")),
    # Django's built-in login/logout/password-reset views
    # (names: login, logout, password_reset, password_reset_done,
    # password_reset_confirm, password_reset_complete)
    path("accounts/", include("django.contrib.auth.urls")),
    path("guests/", include("apps.guests.urls")),
]
