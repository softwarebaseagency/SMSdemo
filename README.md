# Lezan School Management System — interface demo

A clickable, look-and-feel demo of the School Management System proposed for
**Lezan English Private School & Kindergarten**, Erbil. Built by **Base Agency**
to be shown alongside the technical and commercial proposal
(`Base_Agency_Lezan_SMS_Final_Technical_Commercial_Proposal_v1.0.pdf`).

It covers **exactly the ten core modules** named in section 5 of that proposal —
no more, no fewer.

> **This is a visual demo, not a working system.** Every record, mark, invoice
> and name is fabricated for illustration. There is no backend, no database and
> no data entry: buttons that would create or change a record say so instead.

---

## The ten modules

| # | Module | Route | What the demo shows |
|---|--------|-------|---------------------|
| 01 | Admissions & Registration | `#/admissions` | Application pipeline, status flow, document checklist, applications table |
| 02 | Student Records | `#/students` | Permanent student register; a detail drawer with profile, enrolment history, academic and financial tabs |
| 03 | Attendance Management | `#/attendance` | Daily class register, term trend against target, class × day heatmap |
| 04 | Timetable & Class Scheduling | `#/timetable` | Weekly grid by period and day, teacher/room assignment, a flagged conflict |
| 05 | Examinations & Grade Management | `#/exams` | Exam setup with entry-lock status, marks table, grade distribution, report card |
| 06 | Fees & Payment Management | `#/fees` | Collections vs expected, ageing, invoice with previous-year carry-forward, debtor list |
| 07 | Teacher & Staff Records | `#/staff` | Staff profiles, department split, the role and permission matrix |
| 08 | Parent & Student Portal | `#/portal` | Capability switchboard beside a preview of the actual guardian view |
| 09 | Communication & Notifications | `#/comms` | Channel delivery, announcement composer, trigger-driven template library |
| 10 | Operational Reports & Dashboards | `#/reports` | The landing dashboard: KPIs, enrolment, collections, ageing, attendance, audit trail |

Sign-in lands on module 10.

---

## What the demo deliberately proves

Two things the proposal argues for, made visible rather than described:

- **Financial continuity.** Open any student in module 02 and choose the
  *Financial* tab, or see the worked example in module 06. Promotion adds a new
  enrolment record; it never recreates the student, and a previous-year balance
  stays attached to the permanent student ID and is shown separately from
  current-year charges.
- **Least-privilege access.** Module 07 carries the role matrix, module 08 shows
  what a guardian can and cannot reach, and the audit trail on module 10 records
  who changed what.

---

## Running it

**Sign in with any click.** No credentials are checked — press *Sign in*, or pick
one of the four role shortcuts (each lands on the module that role lives in).

Any static web server works:

```bash
# Python
python -m http.server 8080

# Node
npx serve .
```

Then open <http://localhost:8080>.

Opening `index.html` directly from the file system also works — there are no
`fetch` calls and no build step.

---

## Deploying

The site is plain HTML, CSS and JavaScript with **no build step and no external
requests** — no CDN, no Google Fonts, no analytics. Both hosts below serve it
as-is from the repository root.

### GitHub Pages

1. Push the repository to GitHub.
2. **Settings → Pages → Source:** *Deploy from a branch*, branch `main`, folder `/ (root)`.
3. Save. The site appears at `https://<user>.github.io/<repo>/`.

`.nojekyll` is included so Jekyll serves every file untouched.

### Cloudflare Pages

1. **Workers & Pages → Create → Pages → Connect to Git**, pick the repository.
2. **Framework preset:** *None*
   **Build command:** leave empty
   **Build output directory:** `/`
3. Deploy.

Or drag the folder onto **Cloudflare Pages → Upload assets** for a one-off deploy
with no Git repository at all.

---

## Project layout

```
index.html              Sign-in screen
app.html                Application shell (sidebar, top bar, router target)
README.md
.nojekyll               Serve files verbatim on GitHub Pages

static/
  css/
    tokens.css          Design tokens: brand, surfaces, type, space, motion
    app.css             Shell, layout and component styles
    charts.css          Chart marks, tooltips, legends, table twins
    modules.css         Timetable, invoice, report card, portal, roster
    login.css           Sign-in screen
  js/
    icons.js            SVG icon set (one family, 1.75px stroke, no emoji)
    i18n.js             English / Kurdish / Arabic strings and the RTL flip
    data.js             The entire fabricated dataset (seeded, so it is stable)
    charts.js           Hand-rolled SVG charts — no charting library
    ui.js               Cards, stat tiles, tables, drawer, toasts
    app.js              Navigation and the hash router
    views/*.js          One file per module, ten in total
  fonts/                Base Meridion (Latin and Arabic-script cuts)
  img/                  Base Agency logo

assets/                 Brand source material — not used by the site at runtime
```

---

## Notes for whoever picks this up

- **Languages.** English, Kurdish (Sorani) and Arabic, switched from the globe
  icon in the top bar. Kurdish and Arabic flip the whole layout to RTL. Interface
  chrome is translated; record data stays in its source script, as it would in
  the real system. Numeric plots stay left-to-right in every language.
- **Charts** are hand-drawn SVG in `charts.js` — nothing is loaded from a CDN, so
  the demo works offline and behind a restrictive network. Every chart has a
  *Table* toggle, keyboard access (arrow keys read each point), and a tooltip
  that never gates a value.
- **The dataset is seeded** (`mulberry32` in `data.js`), so the demo looks
  identical on every reload and on every machine. Change the seed to reshuffle.
- **Adding a module is not the plan.** The sidebar maps 1:1 to the proposal's ten
  modules. If scope changes, change the proposal first.
- **Accessibility** was built in, not retrofitted: visible focus rings, keyboard
  paths through tables, charts and the drawer, status conveyed by icon and label
  rather than colour alone, and `prefers-reduced-motion` respected throughout.

---

© Base Agency. Prepared for Lezan English Private School & Kindergarten.
Confidential — client use only.
