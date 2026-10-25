<p align="center">
  <img src="static/images/voyage-og.jpg" alt="VOYAGE — Curated journeys" width="100%">
</p>

<p align="center">
  <img src="static/images/voyage-logo.png" alt="VOYAGE" width="200">
</p>

<h3 align="center">Curated journeys. Made unforgettable.</h3>

<p align="center">
  An editorial travel platform for discovering destinations,<br>
  planning a journey, and managing every step of a booking.
</p>

<p align="center">
  <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-5.x-0f5132?style=for-the-badge&logo=django&logoColor=white" alt="Django"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/Adityasonar29/Travel-Agency-Website/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Adityasonar29/Travel-Agency-Website/ci.yml?branch=main&style=for-the-badge&label=CI&logo=githubactions&logoColor=white" alt="CI"></a>
  <a href="#-project-status"><img src="https://img.shields.io/badge/status-active%20prototype-be9958?style=for-the-badge" alt="Status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-be9958?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <a href="#-the-journey"><b>The journey</b></a> &nbsp;·&nbsp;
  <a href="#-product-walkthrough"><b>Walkthrough</b></a> &nbsp;·&nbsp;
  <a href="#-features"><b>Features</b></a> &nbsp;·&nbsp;
  <a href="#-get-started"><b>Get started</b></a> &nbsp;·&nbsp;
  <a href="#-documentation"><b>Docs</b></a>
</p>

<br>

VOYAGE is a Django travel platform for curated journeys and personalised travel requests. Travellers explore destinations, choose a package, submit a booking, pay, receive an invoice, and manage their journey from one account. Administrators get dedicated tools for bookings, destinations, tours, users, and revenue.

<br>

## ✦ The journey

<table align="center">
  <tr>
    <th align="center">01 · Discover</th>
    <th align="center">02 · Choose</th>
    <th align="center">03 · Plan</th>
    <th align="center">04 · Confirm</th>
    <th align="center">05 · Manage</th>
  </tr>
  <tr>
    <td align="center">Explore destinations and tours</td>
    <td align="center">Pick a destination and package</td>
    <td align="center">Add traveller details and preferences</td>
    <td align="center">Review, book, and pay</td>
    <td align="center">Invoices, changes, cancellations, reviews</td>
  </tr>
</table>

<br>

## ✦ Product walkthrough

### Public website

<table align="center">
  <tr>
    <td width="50%" align="center"><img src="docs/assets/home-full.png" alt="VOYAGE home page"><br><sub><b>Home</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/about-us.png" alt="About VOYAGE"><br><sub><b>About</b></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/assets/destinations.png" alt="Destinations page"><br><sub><b>Destinations</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/tours.png" alt="Tours page"><br><sub><b>Tours</b></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/assets/explore-destinations.png" alt="Destination catalogue"><br><sub><b>Destination catalogue</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/tour-detail.png" alt="Amalfi Coast tour detail"><br><sub><b>Tour details</b></sub></td>
  </tr>
</table>

### Account and booking

<table align="center">
  <tr>
    <td width="50%" align="center"><img src="docs/assets/login.png" alt="Login page"><br><sub><b>Sign in</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/register.png" alt="Registration page"><br><sub><b>Create an account</b></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/assets/booking-start.png" alt="Booking start"><br><sub><b>Start a booking</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/booking-tour-selected.png" alt="Booking with selected tour"><br><sub><b>Select a tour</b></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/assets/booking-overview.png" alt="Booking overview"><br><sub><b>Review your booking</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/booking-payment.png" alt="Payment page"><br><sub><b>Payment</b></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/assets/booking-payment-processing.png" alt="Payment processing"><br><sub><b>Payment processing</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/booking-confirmation.png" alt="Booking confirmation"><br><sub><b>Confirmation</b></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/assets/booking-confirmed.png" alt="Confirmed journey"><br><sub><b>Confirmed journey</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/journey-profile.png" alt="Journey on profile"><br><sub><b>Journey in profile</b></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/assets/profile.png" alt="Profile page"><br><sub><b>Profile</b></sub></td>
    <td width="50%" align="center"><img src="docs/assets/review.png" alt="Review submission"><br><sub><b>Leave a review</b></sub></td>
  </tr>
</table>

### Presentation

<p align="center">
  <a href="docs/presentation/VOYAGE-Curated-Journeys.pdf">
    <img src="docs/presentation/voyage-curated-journeys-preview-01.png" alt="VOYAGE presentation cover" width="85%">
  </a>
  <br>
  <sub>📄 <a href="docs/presentation/VOYAGE-Curated-Journeys.pdf"><b>Open the 20-page VOYAGE Curated Journeys presentation</b></a></sub>
</p>

<br>

## ✦ Features

<table>
  <tr>
    <td width="50%" valign="top">

### 🧳 For travellers

- Explore destinations and detailed, curated tour packages
- Book through a validated, multi-step flow with traveller preferences
- Review payment status and receive booking confirmations
- Download invoices; manage or cancel journeys from an account
- Maintain profile details, profile image, and wishlist
- Share feedback through journey reviews

</td>
    <td width="50%" valign="top">

### 🛠️ For administrators

- Monitor users, bookings, tours, destinations, and statuses from the dashboard
- Search bookings and manage booking details and status
- Create, edit, and remove destinations and tours
- Review invoices, revenue summaries, and operational communications
- Manage user accounts and view booking activity

</td>
  </tr>
</table>

<br>

## ✦ Email notifications

Customer and administrator emails share one VOYAGE layout, with consistent typography, spacing, colours, footer information, and responsive behaviour.

<details>
<summary><b>View the notification matrix</b></summary>

<br>

| Event | Recipient | Template | Trigger |
| --- | --- | --- | --- |
| New account | Customer | `emails/welcome.html` | Account creation signal |
| Successful login | Customer | `emails/login_alert.html` | Successful login |
| Booking request received | Customer | `emails/booking_confirmation.html` | Booking creation |
| New booking received | Admin | `emails/admin_booking_notification.html` | Booking creation |
| Payment / journey confirmed | Customer | `emails/booking_confirmed.html` | Successful payment |
| Invoice generated and sent | Customer | `emails/invoice.html` | Invoice send workflow |
| Journey cancellation | Customer | `emails/booking_cancelled.html` | Cancellation POST |
| Refund initiated | Customer | `emails/refund_initiated.html` | Paid booking cancellation |
| Contact acknowledgement | Customer | `emails/contact_auto_reply.html` | Contact form submission |

Reusable templates for future verification, password reset, review, reminder, newsletter, and processed-refund workflows are documented in the [email event matrix](docs/EMAIL-EVENT-MATRIX.md). They are not necessarily active event triggers.

</details>

<br>

## ✦ Project structure

```text
travel-agency-project/
├── .github/workflows/   GitHub Actions CI
├── apps/
│   ├── accounts/        authentication, profiles, wishlist
│   ├── admin_panel/     dashboard and administration
│   ├── booking/         booking, payment, invoices, reviews
│   └── core/            destinations, tours, home, shared utilities
├── config/              Django settings, URLs, WSGI
├── docs/                product, email, and presentation documentation
├── media/               uploaded files and generated invoices
├── static/              CSS, JavaScript, images, loader assets
├── templates/           customer, admin, component, and email templates
└── manage.py
```

<br>

## ✦ Get started

**Requirements:** Python 3.10 or newer · SQLite for local development · a virtual environment

### Install and run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

| | URL |
|---|---|
| 🌐 Customer site | <http://127.0.0.1:8000/> |
| 🛠️ Admin panel | <http://127.0.0.1:8000/admin-panel/> |

### Local email

Print emails in the terminal with Django's console backend:

```powershell
$env:EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
py manage.py runserver
```

All application emails are saved to a database-backed outbound queue first, so web requests never connect to SMTP. Run the worker in a second terminal:

```powershell
py manage.py run_email_worker
```

<details>
<summary><b>How the email queue behaves</b></summary>

<br>

- Failed deliveries retry with exponential backoff, capped at one hour, until delivery succeeds.
- SMTP connections time out after five seconds by default. Set `EMAIL_TIMEOUT` to change this.
- Email logs stay *pending* while queued or retrying, and become *sent* once the backend accepts the message.
- Delivery is **at-least-once**: an abrupt worker failure after provider acceptance but before the database update can send a duplicate email.

</details>

<details>
<summary><b>Deploying on Render</b></summary>

<br>

1. Apply migrations with `python manage.py migrate` before enabling the queue.
2. Keep the existing web service and set its **Start Command** to `sh start.sh`. The script runs Gunicorn and the queue worker in the same service, so no extra service is needed.
3. Use the persistent production database configured by `DATABASE_URL`. Queued messages survive service restarts.
4. Configure a working email backend or provider. Retries cannot deliver mail while the provider is unavailable or misconfigured.

</details>

<br>

## ✦ Checks and tests

Run the same core checks as the GitHub Actions workflow:

```powershell
py manage.py check
py manage.py makemigrations --check --dry-run
py manage.py collectstatic --noinput
py manage.py test
```

The workflow runs on pushes to `main` and on pull requests. See the latest [CI results](https://github.com/Adityasonar29/Travel-Agency-Website/actions/workflows/ci.yml).

<details>
<summary><b>Verify that all email templates compile</b></summary>

<br>

```powershell
py manage.py shell -c "from django.template.loader import get_template; import glob,os; [get_template('emails/'+os.path.basename(f)) for f in glob.glob('templates/emails/*.html')]; print('email templates compile successfully')"
```

</details>

<br>

## ✦ Documentation

| | |
|---|---|
| 📋 [Product Requirements Document](docs/PRD.md) | What VOYAGE does and why |
| 🗺️ [Wireframes & information architecture](docs/WIREFRAMES.md) | Page structure and flows |
| ✉️ [Email event matrix](docs/EMAIL-EVENT-MATRIX.md) | Every email, trigger, and template |
| 🎞️ [Presentation handoff](docs/presentation/README.md) | Notes for the 20-page deck |
| 🤝 [Contribution guide](CONTRIBUTING.md) | How to contribute |

<br>

## ✦ Design principles

- **Editorial** — typography and destination imagery create a sense of discovery.
- **Calm** — warm ivory, charcoal, and restrained champagne-gold accents.
- **Clear** — visible form labels, predictable spacing, timely validation at every booking step.
- **Consistent** — the admin experience shares the brand language while keeping operational tools efficient.

<br>

## ✦ Project status

VOYAGE is an **active prototype**. Before production deployment:

- [ ] Configure a production secret key
- [ ] Disable debug mode and set explicit allowed hosts
- [ ] Use a production database and email provider
- [ ] Review uploaded-file storage
- [ ] Add automated tests for payment idempotency and notification delivery

<br>

<p align="center">
  <sub>Made with care · Released under the <a href="LICENSE">MIT License</a></sub>
</p>