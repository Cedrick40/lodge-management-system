from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Guest
from .forms import GuestForm
# from apps.accounts.decorators import role_required  # your Module 1b decorator

@login_required
def guest_list(request):
    query = request.GET.get("q", "")
    guests = Guest.objects.all()
    if query:
        guests = guests.filter(Q(full_name__icontains=query) | Q(phone__icontains=query))
    return render(request, "guests/guest_list.html", {"guests": guests, "query": query})

@login_required
def guest_create(request):
    if request.method == "POST":
        form = GuestForm(request.POST)
        if form.is_valid():
            guest = form.save()
            return redirect("guests:detail", pk=guest.pk)
    else:
        form = GuestForm()
    return render(request, "guests/guest_form.html", {"form": form, "mode": "create"})

@login_required
def guest_edit(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == "POST":
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            return redirect("guests:detail", pk=guest.pk)
    else:
        form = GuestForm(instance=guest)
    return render(request, "guests/guest_form.html", {"form": form, "mode": "edit", "guest": guest})

@login_required
def guest_detail(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    # Stay history + total spend depend on Reservation/Folio, built in Modules 3–4.
    # Placeholder for now — wire this up once those models exist:
    # reservations = guest.reservation_set.select_related("room", "folio").order_by("-check_in_date")
    # total_spend = sum(r.folio.total() for r in reservations if hasattr(r, "folio"))
    reservations = []
    total_spend = 0
    return render(request, "guests/guest_detail.html", {
        "guest": guest, "reservations": reservations, "total_spend": total_spend,
    })

@login_required
def guest_search_api(request):
    """JSON endpoint for autocomplete — consumed by the Reservation form in Module 3."""
    query = request.GET.get("q", "")
    guests = Guest.objects.filter(
        Q(full_name__icontains=query) | Q(phone__icontains=query)
    )[:10] if query else []
    data = [{"id": g.id, "text": f"{g.full_name} — {g.phone}"} for g in guests]
    return JsonResponse({"results": data})