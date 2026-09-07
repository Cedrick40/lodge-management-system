# Master Prompt: Build a Lodge Management System (Django, 23-Room Lodge, Zambia)

> Copy everything below into your AI coding tool (Claude Code, ChatGPT, a developer brief, etc.) as the starting instruction. It is written so it can be fed in as a single prompt, then followed step by step, module by module.

---

## 1. Project Context

You are building a **Lodge Management System (LMS)** for a boutique lodge in Zambia with **23 rooms**. This is a lean, small-property system — not enterprise hotel-chain software. It must be fast, simple for non-technical front-desk/bar staff to use, and resilient to Zambia's patchy rural internet.

**Confirmed property details:**
- 23 rooms today, but **room count must never be hardcoded** — rooms are dynamic database records. The Owner/GM must be able to add, edit, or remove rooms at any time through an admin screen, without breaking historical bookings, folios, or invoices (see "Dynamic Room Management" rules in Module 1).
- Currently **room-only (bed-only)** billing. A small bar is already operating; a food/meal offering is coming soon — bar charges must post to the guest folio now, and meal-plan rate types must be addable later without a rebuild.
- **No activities offered currently** — no activities/scheduling module in the MVP.
- **Not yet listed on any OTA** — no channel-manager integration in the MVP, but the `Reservation.source` field must exist so this can be added later without re-architecting.
- **Hosting: cloud-hosted.**
- **Payments: Airtel Money and MTN Mobile Money, plus cash.** Card is optional/lower priority.
- **Currency: ZMW (Zambian Kwacha) only.** Hardcode ZMW across all models, views, templates, and invoices — no multi-currency logic needed.
- **Rate structure: two editable rate types per room type.**
  - **Full Night** — e.g. K450, billed for a standard overnight stay.
  - **Short Time** — e.g. K200 for a 4-hour stay (day-use/short stay).
  - Both amounts (and the 4-hour duration) must be **admin-editable settings**, not hardcoded — the Owner/GM should be able to change either price, or the short-time duration, from an admin screen at any time without a code change.
- **Tax: fixed 16% VAT**, configured centrally (not scattered across the codebase).
- **Guest ID capture: omitted for now.** Do not build passport/NRC fields — keep guest intake fast and low-friction (full name, phone, email, optional nationality, notes only).
- **Compliance approach: keep it simple.** Generate correctly formatted VAT-compliant PDF invoices (net + VAT + gross, sequential numbering). No live ZRA Smart Invoice API integration in the MVP — just store data cleanly enough (net amount, VAT amount, gross total, timestamps) that a future ZRA export is a straightforward addition.

---

## 2. Technical Stack & Architectural Guidelines

- **Backend:** Python 3.11+ with **Django 5.x**.
- **Database:** **PostgreSQL** for cloud deployment (primary target); SQLite acceptable for local development only.
- **Frontend:** Responsive HTML5 via **Django Templates**, styled with **Tailwind CSS or Bootstrap 5**, with minimal JavaScript via **Alpine.js or HTMX** for lightweight interactivity (avoid a heavy SPA framework — not needed at this scale).
- **Offline strategy:** Progressive Web App (PWA) using **django-pwa**, a Service Worker for caching core static assets, and a browser-side **IndexedDB queue** for front-desk actions (check-in/out, room status changes) made while offline, auto-syncing to Django REST endpoints on reconnect.
- **Currency:** ZMW hardcoded everywhere — no currency field/selector needed.
- **Tax rate:** 16% VAT, fixed in `settings.py` as a single configurable constant (not hardcoded per view, so a future rate change is a one-line edit).
- **PDF invoices:** WeasyPrint or xhtml2pdf rendering Django templates.
- **Exports:** pandas or openpyxl for CSV/Excel report exports.

---

## 3. Data Schema

Build the schema exactly to this shape (adjust field types as needed, but keep the relationships and the dynamic/soft-delete behavior intact):

```
                  +---------------------------+
                  |         RoomType          |
                  +---------------------------+
                  | name                      |
                  | night_rate (Decimal ZMW)  |
                  | short_time_rate (Decimal) |
                  | short_time_hours (int)    |
                  | is_active (bool)          |
                  +---------------------------+
                                | 1
                                |
                                *
+-------------------+     +---------------------------+     +-------------------+
|       User        |     |           Room            |     |       Guest       |
+-------------------+     +---------------------------+     +-------------------+
| username          |     | room_number               |     | full_name         |
| role               |    | room_type (FK)            |     | phone             |
+-------------------+     | status                    |     | email             |
                          | is_active (soft-delete)   |     | nationality (opt) |
                          | notes                     |     | notes             |
                          +---------------------------+     +-------------------+
                                        | 1                           | 1
                                        |                             |
                                        *                             *
                               +--------------------------------+
                               |          Reservation           |
                               +--------------------------------+
                               | guest (FK)                     |
                               | room (FK)                      |
                               | check_in_date                  |
                               | check_out_date                 |
                               | stay_type (night/short_time)   |
                               | source (walk-in/phone/direct)  |
                               | status                         |
                               +--------------------------------+
                                               | 1
                                               |
                                               *
                               +--------------------------------+
                               |             Folio              |
                               +--------------------------------+
                               | reservation (FK)               |
                               | status                         |
                               +--------------------------------+
                                           | 1             | 1
                                           |               |
                                           *               *
                 +---------------------------+   +---------------------------+
                 |         FolioItem         |   |          Payment          |
                 +---------------------------+   +---------------------------+
                 | folio (FK)                |   | folio (FK)                |
                 | category (room/bar/other) |   | method (cash/airtel/mtn)  |
                 | description               |   | amount (Decimal ZMW)      |
                 | amount (Decimal ZMW)      |   | reference_id              |
                 | tax_amount (Decimal ZMW)  |   +---------------------------+
                 +---------------------------+
```

**Critical rule — Dynamic Room Management:** `Room` and `RoomType` must support full CRUD from an admin UI. Deleting a room must **never** be a hard delete — it must be a **soft delete/archive** (`is_active = False`) so that any past `Reservation`, `Folio`, or `Payment` referencing that room remains intact and historically accurate. Archived rooms simply disappear from the bookable inventory and admin "active rooms" list, but nothing downstream breaks.

---

## 4. Module-by-Module Development Plan

Build in this order. Each module should be functional and testable before moving to the next.

### Module 1: System Setup, Core Models & Dynamic Room Management

**1a. Environment setup (do this first, in VS Code, before any Django code)**

Follow these steps in order to get from a blank machine to a running Django project in VS Code:

1. **Install Python 3.11+**
   - Windows: download from python.org, run the installer, and tick "Add Python to PATH" during install.
   - Mac: `brew install python@3.11` (requires Homebrew), or the python.org installer.
   - Verify: open a terminal and run `python --version` (or `python3 --version` on Mac/Linux) — confirm it shows 3.11 or higher.
2. **Install VS Code** from code.visualstudio.com if not already installed.
3. **Install VS Code extensions** (Extensions panel, `Ctrl+Shift+X` / `Cmd+Shift+X`):
   - **Python** (Microsoft) — language support, linting, debugging.
   - **Pylance** — usually installs alongside Python.
   - **Django** (Baptiste Darthenay or similar) — template/syntax highlighting for `.html` Django templates.
   - **SQLite Viewer** (only needed if using SQLite locally).
4. **Create your project folder and open it in VS Code**
   - `mkdir lodge-management-system && cd lodge-management-system`
   - `code .` (opens the folder in VS Code)
5. **Create and activate a virtual environment** (keeps this project's packages isolated from your system Python)
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
   - In VS Code, select this `venv` as your Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter" → choose the one inside `venv`.
6. **Install Django and core dependencies**
   ```
   pip install django psycopg2-binary python-decouple pillow
   pip install django-pwa weasyprint
   pip install pandas openpyxl
   ```
   - `psycopg2-binary` — PostgreSQL driver.
   - `python-decouple` — keeps secrets (DB password, secret key) out of source code, in a `.env` file.
   - `pillow` — image handling (needed if any image uploads are added later).
   - `django-pwa` — offline/PWA support (Module 8).
   - `weasyprint` — PDF invoice generation (Module 4).
   - `pandas` / `openpyxl` — report exports (Module 7).
7. **Save your dependencies** so they're reproducible: `pip freeze > requirements.txt`
8. **Start the Django project**
   ```
   django-admin startproject lodgesystem .
   ```
   (the trailing `.` creates it in the current folder rather than a nested subfolder)
9. **Install and configure PostgreSQL** (for real/cloud-matching development; SQLite is fine to start with and switch later)
   - Install PostgreSQL locally (postgresql.org) or use a free cloud instance (e.g., from your eventual cloud host) for development.
   - Create a database and user for this project.
   - In `settings.py`, set the `DATABASES` config to use `psycopg2` with credentials loaded via `python-decouple` from a `.env` file (never commit real credentials).
10. **Create the app structure**
    ```
    python manage.py startapp rooms apps/rooms
    python manage.py startapp guests apps/guests
    python manage.py startapp reservations apps/reservations
    python manage.py startapp billing apps/billing
    python manage.py startapp bar_pos apps/bar_pos
    python manage.py startapp housekeeping apps/housekeeping
    ```
    Register each app in `INSTALLED_APPS` in `settings.py`.
11. **Run initial migrations and create a superuser**
    ```
    python manage.py migrate
    python manage.py createsuperuser
    ```
12. **Run the dev server and confirm it works**
    ```
    python manage.py runserver
    ```
    Visit `http://127.0.0.1:8000/admin/` and log in with the superuser to confirm the base project is alive before writing any models.
13. **Set up version control**: `git init`, add a `.gitignore` (exclude `venv/`, `.env`, `__pycache__/`, `*.pyc`, `db.sqlite3`), then commit this baseline before building Module 1's models.

**1b. Core models & dynamic room management**
- Build `RoomType` (name, capacity, `night_rate` in ZMW, `short_time_rate` in ZMW, `short_time_hours`, is_active) and `Room` (room_number, room_type FK, status, is_active, notes) models — night rate and short-time rate/duration must be editable per room type from the Django admin or a dedicated settings screen, never hardcoded in code.
- Build full CRUD views (Create, Read, Update, Delete) allowing the Owner/GM to dynamically add rooms, edit room numbers/types, or **archive (soft-delete)** rooms without touching past financial records.
- Seed the system with a couple of example room types (e.g., Standard at K450/night, K200/short-time) the owner can rename/edit — do not hardcode 23 rooms, or the K450/K200 figures, anywhere in application logic, only as initial seed data.
- Extend Django's `AbstractUser` with a `role` field: `OWNER_GM`, `FRONT_DESK`, `HOUSEKEEPING`, `BAR_STAFF`, `ACCOUNTANT`.
- Write custom Django permission decorators/mixins enforcing the role matrix (Section 5) on every view from the start.

### Module 2: Guest Profiles & Basic Registration
- `Guest` model: `full_name`, `phone`, `email`, `nationality` (optional), `notes`. **No passport/NRC field.**
- Quick-search guest repository by name or phone.
- Auto-complete dropdowns during reservation creation to avoid duplicate guest profiles.
- Guest stay history timeline: past visits and total spend in ZMW.

### Module 3: Reservations & Front Desk Command Center
- Visual booking grid: rooms on the Y-axis, dates on the X-axis, daily/weekly view.
- Click-to-book (or drag-and-drop) assignment of reservations to open rooms.
- Booking creation with `stay_type` (Full Night or Short Time) and `source` field (walk-in, phone, direct — ready for future OTA sources). Selecting Short Time should auto-fill the checkout time based on `RoomType.short_time_hours` from the check-in time, editable by staff if needed.
- Overbooking guard logic (Django signal/validation preventing double-booking the same room/dates, accounting for both night and short-time bookings on the same day).
- 2-click check-in/check-out modal.
- Real-time room status dashboard: Available, Occupied, Dirty, Clean, Maintenance.

### Module 4: Billing, Invoicing & ZMW Payment Processing
- `Folio` model linked 1:1 to each `Reservation`.
- Auto-calculate stay cost in ZMW based on `stay_type`: nights stayed × `RoomType.night_rate` for Full Night bookings, or a flat `RoomType.short_time_rate` for Short Time bookings.
- Support posting additional `FolioItem`s (bar sales, generic extras) to an open folio.
- `Payment` model: method (cash / Airtel Money / MTN Mobile Money / card), amount (ZMW), reference_id for mobile money transaction tracking.
- VAT-compliant PDF invoice generation (WeasyPrint/xhtml2pdf): explicit **Base Price (ZMW) + 16% VAT (ZMW) = Total (ZMW)** breakdown.
- Sequential invoice numbering (e.g., `INV-2026-0001`).
- Refund / voided-charge audit trail.

### Module 5: Bar POS & Room Charging
- `BarCategory` and `BarItem` models (name, price in ZMW, stock quantity).
- Basic stock deduction on sale.
- Touch-friendly POS screen: quick item selection, running basket total.
- "Charge to Room": search active guests by room number or name, post the order as a `FolioItem` (category = `bar`) directly to their bill.

### Module 6: Housekeeping & Maintenance Tracker
- Mobile-friendly task board filtered by room status.
- Single-tap status change (Dirty → Clean) for housekeeping staff.
- Maintenance toggle: setting a room to Maintenance instantly removes it from bookable inventory in Module 3.

### Module 7: Reports & Analytics Dashboard
- Occupancy Rate (%), ADR (ZMW), RevPAR (ZMW).
- Daily Cash/Mobile Money collection ledger grouped by payment method (Airtel Money, MTN Mobile Money, Cash).
- Accounts Receivable report (unsettled balances on active/checked-out folios).
- One-click CSV/Excel export (pandas/openpyxl) for monthly bookkeeping.

### Module 8: PWA, Offline Capability & Sync Queue
- Configure `django-pwa`: web app manifest + service worker, caching core CSS/JS statics.
- Browser-side IndexedDB queue recording front-desk actions (check-ins, room status changes) made while offline.
- Auto-sync queued actions to Django REST endpoints once connectivity is restored.

---

## 5. User Roles & Permissions Matrix

| Role | Reservations | Front Desk | Billing | Reports | Room/Staff Mgmt | Settings |
|---|---|---|---|---|---|---|
| `OWNER_GM` | Full | Full | Full | Full | Full | Full |
| `FRONT_DESK` | Create/Edit | Full | View/Create charges | Basic (daily) | None | None |
| `HOUSEKEEPING` | None | Room status only | None | None | None | None |
| `BAR_STAFF` | None | None | Post charges to room | None | None | None |
| `ACCOUNTANT` | View | View | Full | Full | None | None |

Enforce this via Django permission decorators/mixins on every view — do not retrofit later.

---

## 6. Non-Functional Requirements
- **Offline resilience:** front-desk check-in/out and room status changes must queue locally and sync automatically on reconnect (Module 8).
- **Security:** role-based access control, encrypted storage of any sensitive data, audit logs of who changed what and when.
- **Backups:** automatic daily backups on the cloud host, with a documented restore procedure.
- **Performance:** fast on modest tablets/hardware and slow rural internet — keep JS minimal (Alpine.js/HTMX only, no heavy SPA framework).
- **UI simplicity:** large touch-friendly buttons for front-desk/bar tablet use; minimal training required.
- **Never hardcode room count or room list** — everything driven from the `Room`/`RoomType` tables.

---

## 7. Testing & Rollout
1. Simulate a full 23-room month with overlapping bookings, cancellations, and walk-ins.
2. Front-desk stress test: check-in/out 10 guests back-to-back to confirm workflow speed.
3. Explicitly test offline mode — disconnect network mid-session, confirm actions queue and sync correctly afterward.
4. Test the dynamic room CRUD: add a room, archive a room, and confirm past reservations/folios/invoices referencing the archived room remain fully intact and readable.
5. Pilot with real front-desk and bar staff before full rollout; capture friction points.
6. Prepare a 1–2 page staff training guide with screenshots.

---

## 8. Future-Proofing Matrix (do not build now — just don't block these later)

| Feature | How the Current Design Prepares For It |
|---|---|
| Adding/removing rooms | Rooms are dynamic DB rows, not hardcoded constants; soft-delete/archive keeps history intact. |
| Adding food/meal plans | `RoomType`/rate logic is flexible enough to add a `plan_type` (B&B, Half-Board, Full-Board) later. |
| OTAs (Booking.com, etc.) | `Reservation.source` field already exists; a channel-manager integration app can insert into it later. |
| ZRA Smart Invoice API | `FolioItem`/`Payment` store net, VAT, and gross amounts cleanly, making a future JSON export to ZRA straightforward. |
| Multi-currency (if ever needed) | Would require adding a currency field to rate/payment models — not needed now since ZMW-only is confirmed. |
| Passport/NRC capture (if ever needed) | `Guest` model can have the field added later without disrupting existing records. |

---

*This prompt is scoped for a small, 23-room independent lodge running on Django, ZMW-only, with a bar and no activities/OTA/ID-capture requirements yet. When ready to add a meal plan, list on OTAs, or capture guest IDs, extend the relevant module using the Future-Proofing Matrix above rather than starting over.*
