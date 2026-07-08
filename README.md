# Patient Care PWA

An offline-first Progressive Web App for home nursing care of a tube-fed (NGT) patient:
tube-feeding protocol, a date-aware medication checklist, a caregiver report, and a
password-protected admin audit dashboard. Built with **vanilla HTML/CSS/JS** — no build
step, no framework.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The entire app (UI, logic, i18n, data layer) |
| `sw.js` | Service worker — app-shell caching + notifications |
| `manifest.json` | PWA install metadata (icons embedded as SVG data URIs) |

## Features

- **Patient** — profile fields + a print-ready **Emergency Card** for paramedics (diagnosis
  summary, active meds, HMC – RH Rumailah, big red **CALL 999** banner).
- **Today** — 6 feeding sessions/day (every 4 h, start time configurable). Each session is
  5 sequential, order-locked steps (feed → flush → rest → water → rest) with live 1-hour
  timers and Food (900 ml) / Water (1000 ml) progress bars.
- **Medications** — permanent *crush thoroughly* warning, PRN suppository (with 48 h
  no-BM alert), a **date-aware checklist** that auto-builds by the day (daily slots,
  Sunday-only glucose, monthly Vitamin D on its due date), NGT sub-checks
  (crushed / flush), missed-yesterday badges, and a live-countdown **Upcoming Reminders**
  card (NGT change, T-Tube change, Vitamin D, next glucose).
- **Report** — today's summary + timestamped activity log, printable/exportable.
- **Admin** (password-protected) — today's timeline, history browser with date-range /
  caregiver / action-type filters, per-caregiver totals, CSV export, printable report,
  and settings (password, Supabase URL/key + copy-SQL button, feeding start time).

## Data

Every action is logged with **action, timestamp, and nurse name**. Data is written to
**Supabase** when configured and always mirrored to **localStorage**, so the app works
fully offline and falls back gracefully when there is no connection.

## Deploy

1. **Netlify** — drag-and-drop this folder, or connect the repo (no build command;
   publish directory = repo root). HTTPS is required for the service worker and install.
2. **Supabase** — create a project, open **Admin → Settings**, paste the Project URL and
   anon key, click **Copy SQL Schema**, run it in the Supabase SQL editor (it creates the
   tables and enables RLS with permissive public policies), then **Save & Connect**.

## First run

1. Open the app and enter the **nurse name** in the header (persists across sessions).
2. Tap **🔔** to allow reminders (30 min before + at each feeding/medication slot).
3. Open **Admin** to set the admin password on first use.
4. Toggle **🌐 AR/EN** for Arabic (RTL) or English (LTR).
