# focus-adaptive-dashboard

**FocusForge** is an adaptive study analytics dashboard for high schoolers.
Instead of just blocking distractions, it analyzes metrics like session times
and attention decay to map a student's optimal focus windows. Built for
accessibility, it features toggleable UI modes for ADHD focus and
colorblind-friendly data visualization.

Originally a single-file Streamlit prototype, it is now a split application:

| Layer    | Stack                                  | Dev port |
| -------- | -------------------------------------- | -------- |
| Backend  | Flask + Flask-SQLAlchemy + SQLite      | `:5000`  |
| Frontend | Vue 3 (`<script setup>`) + Vite + Pinia | `:5173`  |

Sessions now persist in a database instead of vanishing on refresh.

## Quick start

```bash
# 1. Backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/flask --app backend seed        # create tables, load the sample CSV

# 2. Frontend
cd frontend && npm install && cd ..
```

Then run both processes:

```bash
# terminal 1 — API
.venv/bin/flask --app backend --debug run

# terminal 2 — Vite dev server with HMR
cd frontend && npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` to Flask on `:5000`, so the
browser sees a single origin and CORS never comes up in development.

## Layout

```
backend/
  __init__.py    create_app() factory, error handlers, SPA catch-all
  config.py      DATABASE_URL-driven config
  models.py      Subject, StudySession, shared value bounds
  validation.py  request payload checks -> 400s
  csv_io.py      CSV import/export shared by the API and the seed CLI
  seed.py        flask CLI: seed / init-db / reset-db
  api/           subjects, sessions, analytics, data blueprints
frontend/
  src/api        fetch wrapper
  src/stores     Pinia: study data, accessibility preferences
  src/components forms, KPI cards, Plotly wrapper, charts, sprint timer
  src/views      StandardDashboard, AdhdDashboard
  src/styles     base.css + adhd.css
legacy/
  streamlit_app.py   the original prototype, kept runnable for reference
```

## API

| Method   | Path                     | Purpose                                    |
| -------- | ------------------------ | ------------------------------------------ |
| `GET`    | `/api/subjects`          | courses with session counts                |
| `POST`   | `/api/subjects`          | add a course (`409` if it already exists)  |
| `DELETE` | `/api/subjects/<id>`     | remove a course and its sessions           |
| `GET`    | `/api/sessions`          | logged sessions (`?subject_id=` to filter) |
| `POST`   | `/api/sessions`          | log a session                              |
| `DELETE` | `/api/sessions/<id>`     | remove a session                           |
| `GET`    | `/api/analytics/summary` | KPIs plus all four chart datasets          |
| `GET`    | `/api/data/export`       | download `focusforge_database.csv`         |
| `POST`   | `/api/data/import`       | restore from a CSV (multipart `file`)      |

Errors come back as `{"error": "..."}`. Value ranges live in one place —
`BOUNDS` in [backend/models.py](backend/models.py) — and are enforced by request
validation, CSV import and database check constraints alike.

### CSV format

Unchanged from the Streamlit version, so old exports still restore:

```
Date,Hour,Subject,Duration_Min,Distractions,Focus_Rating
2026-05-15,19,Math,51,3,4
```

Imports are all-or-nothing: one bad row rejects the whole file and leaves the
database untouched. Courses named in the file but missing from the database are
created automatically.

## CLI

```bash
flask --app backend seed          # tables + default courses + sample sessions
flask --app backend seed --force  # re-import the sample CSV over existing data
flask --app backend init-db       # tables only
flask --app backend reset-db      # drop everything and recreate
```

## Accessibility

- **ADHD Focus Mode** swaps in a low-friction layout (one chart plus a real
  countdown timer), scales up type and line spacing, and renders body copy in
  bionic style — the first half of each word bolded as an eye anchor.
- **Colorblind Safe Mode** repaints every chart in the Okabe–Ito barrier-free
  palette and switches the sequential scale from Oranges to Viridis.

Both toggles persist to `localStorage`.

## Production build

```bash
cd frontend && npm run build      # -> frontend/dist
.venv/bin/flask --app backend run # serves the SPA and the API on :5000
```

`create_app()` serves `frontend/dist` when it exists, with a catch-all that
returns `index.html` for client routes while unknown `/api/*` paths still 404 as
JSON. For a real deployment use `gunicorn backend.wsgi:app`.

Charts use `plotly.js-basic-dist-min` (~411 kB gzipped in the bundle) rather
than the full distribution — it carries the `bar` and `scatter` traces, which is
everything these charts need.

Point at Postgres instead of SQLite by setting `DATABASE_URL`.

## Legacy prototype

The original Streamlit app is preserved at
[legacy/streamlit_app.py](legacy/streamlit_app.py) and still runs:

```bash
pip install -r legacy/requirements.txt
streamlit run legacy/streamlit_app.py
```

It keeps everything in memory, so its data is lost on refresh. One number
legitimately differs between the two: its "Total Combined Minutes Studied" chart
plotted raw un-aggregated rows despite the title; the new dashboard sums them.
