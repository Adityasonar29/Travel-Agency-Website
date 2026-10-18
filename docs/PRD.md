# VOYAGE Product Requirements Document

## 1. Product definition

VOYAGE is a travel discovery and booking product for people who want curated trips without the visual noise of a conventional booking marketplace. The customer site turns destination inspiration into a structured journey request. The admin panel gives the travel team the tools to curate inventory, manage bookings, monitor revenue, and communicate with travellers.

## 2. Product goals

### Primary goals

1. Make it easy to move from destination inspiration to a selected journey.
2. Collect enough traveller context to create a useful booking request.
3. Give travellers confidence through review, payment, confirmation, and invoice states.
4. Give administrators a reliable view of inventory and booking operations.
5. Keep every customer touchpoint visually consistent with the VOYAGE brand.

### Non-goals

- VOYAGE is not intended to become a real-time airline or hotel inventory marketplace.
- The current payment flow is a project payment experience and must be hardened before production use.
- The admin panel is operational software, not a separate enterprise design system.

## 3. Personas

### Traveller

Needs inspiration, clarity about package details, an easy booking form, a safe confirmation path, and access to journey records after submission.

### Travel administrator

Needs to maintain destinations and tours, review booking details, update statuses, inspect invoices, understand revenue movement, and resolve customer requests quickly.

## 4. Key journeys

### Curated booking

1. Traveller opens the destination catalogue.
2. Traveller opens a destination or tour.
3. Traveller clicks **Book Now** and arrives at booking with that package selected.
4. Traveller enters personal and travel details.
5. Traveller sets budget, travel style, and special requests.
6. Traveller reviews the booking.
7. System prevents duplicate submissions.
8. System sends a booking-received message.
9. Traveller completes payment.
10. System creates an invoice, sends confirmation, and exposes the journey detail.

### Cancellation

1. Authenticated traveller opens a journey.
2. Traveller confirms cancellation through the confirmation dialog.
3. System updates booking and payment/refund state once.
4. System shows the branded loading overlay while the request completes.
5. System sends cancellation and, where relevant, refund-initiated email.

### Administration

1. Administrator signs in.
2. Dashboard shows operational counts and revenue activity.
3. Administrator searches or filters bookings.
4. Administrator opens a booking to inspect details and update status.
5. Administrator creates or edits tours and destinations through structured form sections.
6. Administrator opens generated invoice PDFs from the invoice list.

## 5. Functional requirements

| Area | Requirement | Acceptance signal |
| --- | --- | --- |
| Discovery | Show destinations and curated tours with useful imagery and summaries | Cards link to valid detail pages |
| Booking | Preserve the selected tour when Book Now routes to booking | Selected package is present on booking form |
| Validation | Identify missing required fields below the relevant control | User can correct the field without guessing |
| Idempotency | Avoid duplicate booking creation from repeated clicks or requests | One user action produces one booking |
| Payment | Show progress feedback during payment and redirect to confirmation | Overlay disappears after completion or failure |
| Invoice | Generate an invoice from booking data | PDF contains consistent customer, trip, and payment data |
| Cancellation | Update state once and communicate refund status | Booking and email agree on status |
| Admin CRUD | Create and edit tours and destinations with consistent layouts | Labels sit above controls; uploads remain functional |
| Email | Send active event notifications with real context | Event matrix maps trigger to recipient and template |
| Error handling | Use branded 404 output for unknown routes and missing records | Response status is 404 and page is branded |

## 6. Quality attributes

- Responsive from 375px through desktop widths.
- Accessible labels, focus states, keyboard-friendly native controls, and readable error text.
- No horizontal overflow from long URLs, filenames, or form values.
- Email templates render without external fonts or stylesheets.
- Payment and booking actions remain safe if the mail provider is unavailable.
- Production deployment must disable debug mode and protect credentials.

## 7. Success measures

- Fewer incomplete booking submissions caused by unclear required fields.
- No duplicate bookings from repeated submit actions.
- Every paid booking has a matching invoice and confirmation event.
- Administrators can complete tour and destination CRUD without layout ambiguity.
- Travellers can locate a journey and its invoice from the account area.

## 8. Open product work

- Add automated integration tests around payment idempotency and email dispatch.
- Add a formal password reset and email verification flow if those templates become customer-facing.
- Add a persistent notification delivery log for retries and support visibility.
- Replace development email credentials and debug settings before production.
