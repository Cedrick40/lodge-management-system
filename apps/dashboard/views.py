from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    """
    The front page after login. Right now it's a shell -- the real
    numbers (today's arrivals/departures, occupied rooms, outstanding
    balances) get wired in once Reservations (Module 3) and Billing
    (Module 4) exist to query. No role restriction here: everyone who
    can log in should see the dashboard, just with different content
    depending on their role once those modules are built.
    """

    template_name = "dashboard/home.html"