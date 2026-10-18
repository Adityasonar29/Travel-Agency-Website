# VOYAGE Wireframing and Information Architecture

This document records the intended structure of the primary screens. It is a low-fidelity implementation guide, not a visual specification. Typography, spacing, and color should follow the existing VOYAGE design tokens.

## Global shell

```text
┌─────────────────────────────────────────────────────────────┐
│ VOYAGE                         Login  Register          Menu │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Page heading                            │
│                 Short supporting copy                       │
│                                                             │
│                    Page content                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The shell separates brand navigation from content, preserves generous top space, and keeps the mobile menu available without changing the information hierarchy.

## Destination catalogue

```text
┌─────────────────────────────────────────────────────────────┐
│ Explore the World                                           │
│                                                             │
│                 SIGNATURE DESTINATIONS                      │
│                 Where Will You Go?                          │
│                                                             │
│       [ Destination card ] [ Destination card ]             │
│       [ Destination card ] [ Destination card ]             │
└─────────────────────────────────────────────────────────────┘
```

Each card should expose destination identity, image, short context, and a clear route to detail.

## Booking flow

```text
Step 1                 Step 2                 Step 3
Choose Journey  →      Travel Details  →     Preferences
Destination            Name, email, date      Budget, style
Tour package            travellers             requests
                                  ↓
                         Review Your Booking
                         Confirm Booking
```

### Step 1: Choose Journey

- Destination selector or destination input.
- Tour package selector.
- Continue action.
- Required-field messages below controls.

### Step 2: Travel Details

- Full name and email in a two-column desktop grid.
- Phone and travel date in a two-column desktop grid.
- Number of travellers as a full-width numeric control.
- Back and Continue actions in a separated bottom action row.

### Step 3: Preferences

- Budget range and travel style.
- Special requests textarea.
- Back and Continue actions.

### Review

- Selected package and destination.
- Date, guest name, and traveller count.
- One clear confirmation action.
- Branded loading overlay during submission.

## Journey detail

```text
┌─────────────────────────────────────────────────────────────┐
│ Booking ID                                                   │
│ Journey name                                                 │
│                                                             │
│ Guest              Status              Travel date           │
│ Journey value      Invoice              Cancellation         │
│                                                             │
│ Booking information                                         │
│ label / value rows                                          │
└─────────────────────────────────────────────────────────────┘
```

The detail view is the traveller's source of truth after booking. Values must come from the booking record and status changes must be visible.

## Admin dashboard

```text
┌──────────────┬──────────────────────────────────────────────┐
│ VOYAGE       │ Profile  View Website  A Aditya              │
│              ├──────────────────────────────────────────────┤
│ Dashboard    │ Dashboard                                    │
│ Bookings     │ [Users] [Bookings] [Tours] [Destinations]    │
│ Users        │ [Confirmed] [Pending] [Completed] [Cancelled]│
│ Tours        │ Recent bookings table                        │
│ Destinations │ Revenue chart                                │
└──────────────┴──────────────────────────────────────────────┘
```

## Admin forms

```text
Breadcrumb
Large editorial title
Short description
Back action

┌─────────────────────────────────────────────────────────────┐
│ Section heading                                             │
│ Label                                                        │
│ [Input]                  Label                              │
│                         [Input]                             │
│                                                             │
│ Section heading                                             │
│ [two-column form grid]                                      │
│                                                             │
│─────────────────────────────────────────────────────────────│
│ Cancel                                      Save / Create    │
└─────────────────────────────────────────────────────────────┘
```

Every label sits above its field. File uploads remain real Django inputs, image previews stay contained, multi-selects stay compact, and actions are grouped at the bottom.

## Responsive behavior

- At desktop widths, use two-column form grids and a persistent admin sidebar.
- At tablet widths, tighten page padding and retain readable field widths.
- At mobile widths, collapse grids to one column, preserve readable labels, and keep primary actions reachable.
- Never allow a URL, filename, table cell, or email value to force horizontal overflow.
