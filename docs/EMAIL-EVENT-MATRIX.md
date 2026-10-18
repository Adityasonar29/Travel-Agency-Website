# Email Event Matrix

This matrix distinguishes templates that the current application actively sends from templates that are prepared for future workflows.

## Active notifications

| Event | Trigger location | Recipient | Template | Data currently passed |
| --- | --- | --- | --- | --- |
| Welcome | `apps/accounts/signals.py` after user creation | New user | `welcome.html` | Name and user object |
| Login alert | `apps/accounts/views.py` after successful authentication | Signed-in user | `login_alert.html` | Name, time, IP, user agent, profile URL |
| Booking received | `apps/booking/views.py::_send_booking_emails` | Traveller | `booking_confirmation.html` | Booking ID, tour, destination, date, travellers, value, status |
| Admin booking notice | Same booking event | Site owner | `admin_booking_notification.html` | Booking ID, customer, tour, status, amount |
| Payment confirmation | `apps/booking/views.py::_send_payment_success_email` | Traveller | `booking_confirmed.html` | Booking, journey, date, travellers, payment method, transaction, invoice URL |
| Invoice | `apps/booking/models.py::send_invoice` | Traveller | `invoice.html` | Invoice number, booking, tour, destination, date, travellers, amount, payment |
| Cancellation | `apps/booking/views.py::cancel_booking` | Traveller | `booking_cancelled.html` | Booking, journey, date, amount, refund state, support email |
| Refund initiated | Same cancellation event for paid bookings | Traveller | `refund_initiated.html` | Booking ID, amount, support email |
| Contact acknowledgement | `apps/core/views.py` contact form | Contact sender | `contact_auto_reply.html` | Name, subject, message, site URL |

## Prepared but not currently triggered

These templates remain intentionally available as reusable designs, but the current codebase has no corresponding event handler or route:

| Template | Missing event implementation |
| --- | --- |
| `email_verification.html` | Registration currently activates the account without a verification step |
| `password_reset.html` | No password-reset route currently exists |
| `payment_confirmation.html` | The final payment flow uses the richer `booking_confirmed.html` template |
| `refund_processed.html` | No refund-provider callback or admin refund-completion event exists |
| `review_request.html` | Review page exists, but no scheduled post-trip sender exists |
| `trip_reminder.html` | No scheduled reminder job exists |
| `newsletter.html` | No subscription or campaign sender exists |

This distinction prevents silent assumptions. A template file alone does not send an email; an event handler must call the mailer with the correct context.

## Delivery rules

- Booking and payment workflows catch email failures so a mail outage does not create a duplicate booking or make a successful payment appear to fail.
- Use Django's console or locmem backend during development.
- Do not test against production SMTP with real customer addresses.
- Add a delivery log and retry strategy before treating email as a production-critical audit trail.
