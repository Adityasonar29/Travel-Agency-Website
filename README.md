<div align="center">

<img src="static/images/voyage-logo.png" alt="VOYAGE" width="220">

# Curated journeys. Made unforgettable.

An editorial travel experience for discovering destinations, planning a journey, and managing every step of a booking.

[![Django](https://img.shields.io/badge/Django-5.x-0f5132?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![CI](https://github.com/Adityasonar29/Travel-Agency-Website/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Adityasonar29/Travel-Agency-Website/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/status-active%20prototype-be9958?style=flat-square)](#project-status)
[![License](https://img.shields.io/badge/license-MIT-be9958?style=flat-square)](LICENSE)

</div>

---

VOYAGE is a Django travel platform for curated journeys and personalised travel requests. Travellers can explore destinations, choose a package, submit a booking, pay, receive an invoice, and manage their journey from an account. Administrators have dedicated tools for managing bookings, destinations, tours, users, and revenue.

## Contents

- [The journey](#the-journey)
- [Product walkthrough](#product-walkthrough)
- [What you can do](#what-you-can-do)
- [Email notifications](#email-notifications)
- [Project structure](#project-structure)
- [Get started](#get-started)
- [Checks and tests](#checks-and-tests)
- [Documentation](#documentation)
- [Design principles](#design-principles)
- [Project status](#project-status)

## The journey

| Discover | Choose | Plan | Confirm | Manage |
| --- | --- | --- | --- | --- |
| Explore destinations and tours | Pick a destination and package | Add traveller details and preferences | Review, book, and pay | Access invoices, manage, cancel, or review |

## Product walkthrough

### Public website

| Home | About |
|:---:|:---:|
| ![VOYAGE home page](docs/assets/home-full.png) | ![About VOYAGE](docs/assets/about-us.png) |

| Destinations | Tours |
|:---:|:---:|
| ![Destinations page](docs/assets/destinations.png) | ![Tours page](docs/assets/tours.png) |

| Destination catalogue | Tour details |
|:---:|:---:|
| ![Destination catalogue](docs/assets/explore-destinations.png) | ![Amalfi Coast tour detail](docs/assets/tour-detail.png) |

### Account and booking

| Sign in | Create an account |
|:---:|:---:|
| ![Login page](docs/assets/login.png) | ![Registration page](docs/assets/register.png) |

| Start a booking | Select a tour |
|:---:|:---:|
| ![Booking start](docs/assets/booking-start.png) | ![Booking with selected tour](docs/assets/booking-tour-selected.png) |

| Review your booking | Payment |
|:---:|:---:|
| ![Booking overview](docs/assets/booking-overview.png) | ![Payment page](docs/assets/booking-payment.png) |

| Payment processing | Confirmation |
|:---:|:---:|
| ![Payment processing](docs/assets/booking-payment-processing.png) | ![Booking confirmation](docs/assets/booking-confirmation.png) |

| Confirmed journey | Journey in profile |
|:---:|:---:|
| ![Confirmed journey](docs/assets/booking-confirmed.png) | ![Journey on profile](docs/assets/journey-profile.png) |

| Profile | Leave a review |
|:---:|:---:|
| ![Profile page](docs/assets/profile.png) | ![Review submission](docs/assets/review.png) |

### Presentation

Explore the [20-page VOYAGE Curated Journeys presentation](docs/presentation/VOYAGE-Curated-Journeys.pdf).

![VOYAGE presentation cover](docs/presentation/voyage-curated-journeys-preview-01.png)

## What you can do

### For travellers

- Explore destinations and detailed, curated tour packages.
- Book a package through a validated, multi-step flow with traveller preferences.
- Review payment status and receive booking confirmations.
- Download invoices and manage or cancel journeys from an account.
- Maintain profile details, profile image, and wishlist.
- Share feedback through journey reviews.

### For administrators

- Monitor users, bookings, tours, destinations, and booking statuses from the dashboard.
- Search bookings and manage booking details and status.
- Create, edit, and remove destinations and tours.
- Review invoices, revenue summaries, and operational communications.
- Manage user accounts and view booking activity.

## Email notifications

Customer and administrator notifications share a VOYAGE email layout for consistent typography, spacing, colors, footer information, and responsive behavior.

| Event | Recipient | Template | Trigger |
| --- | --- | --- | --- |
| New account | Customer | `emails/welcome.html` | Account creation signal |
| Successful login | Customer | `emails/login_alert.html` | Successful login |
| Booking request received | Customer | `emails/booking_confirmation.html` | Booking creation |
| New booking received | Admin | `emails/admin_booking_notification.html` | Booking creation |
| Payment/journey confirmed | Customer | `emails/booking_confirmed.html` | Successful payment |
| Invoice generated and sent | Customer | `emails/invoice.html` | Invoice send workflow |
| Journey cancellation | Customer | `emails/booking_cancelled.html` | Cancellation POST |
| Refund initiated | Customer | `emails/refund_initiated.html` | Paid booking cancellation |
| Contact acknowledgement | Customer | `emails/contact_auto_reply.html` | Contact form submission |

Reusable templates for future verification, password reset, review, reminder, newsletter, and processed-refund workflows are documented in the [email event matrix](docs/EMAIL-EVENT-MATRIX.md). These templates are not necessarily active event triggers.

## Project structure

```text
travel-agency-project/
├── .github/workflows/  GitHub Actions CI
├── apps/
│   ├── accounts/       authentication, profiles, wishlist
│   ├── admin_panel/    dashboard and administration
│   ├── booking/        booking, payment, invoices, reviews
│   └── core/           destinations, tours, home, shared utilities
├── config/             Django settings, URLs, WSGI
├── docs/               product, email, and presentation documentation
├── media/              uploaded files and generated invoices
├── static/             CSS, JavaScript, images, loader assets
├── templates/          customer, admin, component, and email templates
└── manage.py
```

## Get started

### Requirements

- Python 3.10 or newer
- SQLite for local development
- A virtual environment

### Install and run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

Open the customer site at `http://127.0.0.1:8000/`. The VOYAGE admin panel is available at `http://127.0.0.1:8000/admin-panel/`.

For local email development, use Django's console backend to print messages in the terminal:

```powershell
$env:EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
py manage.py runserver
```

All application emails are first saved to the database-backed outbound queue; web requests do not connect to SMTP. Run the worker in a second terminal alongside the web server:

```powershell
py manage.py run_email_worker
```

The worker retries failed deliveries with exponential backoff, capped at one hour, and continues retrying until delivery succeeds. SMTP connections time out after five seconds by default; configure `EMAIL_TIMEOUT` to change that limit. Email logs stay pending while queued or retrying and become sent after the email backend accepts the message. Delivery is at-least-once: an abrupt worker failure after provider acceptance but before the database update can result in a duplicate email.

For Render, apply database migrations with `python manage.py migrate` before enabling the queue, then keep the existing web service and set its Start Command to `sh start.sh`. The script runs Gunicorn and the queue worker in the same service, so no additional service is required. Use the persistent production database configured by `DATABASE_URL`; queued messages survive service restarts. Configure a working email backend/provider as well: retries cannot deliver mail while the provider is unavailable or misconfigured.

## Checks and tests

Run the same core checks used by the GitHub Actions workflow:

```powershell
py manage.py check
py manage.py makemigrations --check --dry-run
py manage.py collectstatic --noinput
py manage.py test
```

The workflow runs on pushes to `main` and on pull requests. See [CI results](https://github.com/Adityasonar29/Travel-Agency-Website/actions/workflows/ci.yml).

To compile the email templates through Django's template loader:

```powershell
py manage.py shell -c "from django.template.loader import get_template; import glob,os; [get_template('emails/'+os.path.basename(f)) for f in glob.glob('templates/emails/*.html')]; print('email templates compile successfully')"
```

## Documentation

- [Product Requirements Document](docs/PRD.md)
- [Wireframing and information architecture](docs/WIREFRAMES.md)
- [Email event matrix](docs/EMAIL-EVENT-MATRIX.md)
- [Presentation handoff](docs/presentation/README.md)
- [Contribution guide](CONTRIBUTING.md)

## Design principles

- Editorial typography and destination imagery create a sense of discovery.
- Warm ivory, charcoal, and restrained champagne-gold accents keep the interface calm.
- Forms use visible labels and predictable spacing.
- Clear actions and timely validation guide each booking step.
- The admin experience shares the brand language while keeping operational tools efficient.

## Project status

VOYAGE is an active project prototype. Before production deployment, configure a production secret key, disable debug mode, set explicit allowed hosts, use a production database and email provider, review uploaded-file storage, and add automated tests for payment idempotency and notification delivery.
