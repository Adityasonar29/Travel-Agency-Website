# Contributing to VOYAGE

Thank you for helping improve VOYAGE. Contributions should preserve both the product behavior and the quiet editorial character of the interface.

## Before you start

1. Read the [README](README.md) and the [Product Requirements Document](docs/PRD.md).
2. Check the existing app, template, and static-file structure before creating new files.
3. Keep changes scoped to the requested feature. Avoid changing the database schema or shared styles for a page-specific issue.
4. Check the working tree before editing so existing user changes remain intact.

## Branches and commits

Use a short branch name such as `codex/booking-email-fix` or `feature/admin-destination-form`.

Prefer focused commits:

- `feat: add booking confirmation email`
- `fix: prevent duplicate booking submission`
- `style: refine admin tour form`
- `docs: update product walkthrough`

## Django conventions

- Put domain behavior in the relevant app instead of a global utility.
- Reuse existing forms, models, authentication, CSRF protection, and URL names.
- Keep email context explicit and use real model fields. Do not hardcode customer, tour, payment, or invoice values in templates.
- Keep user-facing email failures from blocking the primary action unless the action itself requires the email to succeed.
- Preserve multipart form encoding for image uploads.
- Use field-level validation messages below the relevant field.

## Frontend conventions

- Use the existing VOYAGE tokens: warm ivory, charcoal, secondary gray, champagne gold, and thin warm borders.
- Scope admin styles to admin components and form classes.
- Keep labels above fields and avoid relying on inherited layout rules.
- Make loading, error, and success states accessible and keyboard-safe.
- Prefer progressive enhancement over a new frontend dependency.

## Email changes

When adding or changing an email:

1. Add or update the template under `templates/emails/`.
2. Extend `emails/base.html`.
3. Add the exact event trigger to the event matrix.
4. Pass real context from the view, model, signal, or task.
5. Test with Django's console or locmem email backend. Do not send real mail during development.
6. Confirm that a mail-provider failure does not create a duplicate booking or payment.

## Verification checklist

```powershell
py manage.py check
py manage.py test
py -m compileall -q apps
```

For UI changes, verify desktop and mobile widths. For email changes, compile every email template and render the changed template with representative context.

## Pull requests

A useful pull request includes:

- What changed and why.
- The user flow affected.
- Screenshots or a short recording for visual changes.
- Test commands and results.
- Any configuration or migration steps.
- Known limitations or follow-up work.
