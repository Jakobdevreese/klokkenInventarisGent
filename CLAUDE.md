# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Django web application cataloguing the carillons, swinging bells, time bells and church bells of Ghent, Belgium — both existing and lost. Domain-facing text (model `verbose_name`s, templates, use cases) is in **Dutch**; code identifiers are in English.

The goal is a system where bell enthusiasts can store the information they collect about bells in a **structured yet flexible** way, and where others can **search it in a modern way**. It is being built as a **prototype to run on the author's home server** for testing. A lightweight in-site **comment/feedback system for testers** is a desired-but-optional feature.

The project is early-stage: the data model and admin are built out, but the public views are still placeholder stubs.

## Layout

- `campanarium/` — the Django project root (contains `manage.py`); **run all Django commands from here**.
  - `campanarium/campanarium/` — settings package (`settings.py`, `urls.py`, `wsgi.py`/`asgi.py`).
  - `campanarium/inventory/` — the single app holding all models, admin, views and templates.
- `analysis/` — design artifacts, not code: the ERD (`erd_inventaris_gent.drawio`/`.svg`), use cases (`use_cases/UC*.md`), and a LaTeX academic article (`article/`).
- `myvenv/` — the local virtualenv (git-ignored).

## Commands

All Django commands run from the `campanarium/` directory with the venv active (`source myvenv/bin/activate`):

```bash
python manage.py runserver          # dev server
python manage.py makemigrations     # after model changes
python manage.py migrate
python manage.py createsuperuser     # admin access at /admin
python manage.py collectstatic
python manage.py test inventory                                   # run app tests
python manage.py test inventory.tests.ClassName.test_method       # single test
```

Build the article: `cd analysis/article && make` (requires `xelatex` + `bibtex`).

Install Python dependencies with `pip install -r requirements.txt` (Django + `psycopg2-binary`). GeoDjango additionally needs the native geospatial stack and a PostGIS-enabled PostgreSQL server (see below).

## GeoDjango / SpatiaLite

This is the main environmental gotcha. The database backend is `django.contrib.gis.db.backends.postgis` (**PostgreSQL + PostGIS**), and `Tower.geo_coordinates` is a `PointField`. Running the server, migrations, or tests requires the native geospatial libraries — **GDAL, GEOS, PROJ** — plus a PostgreSQL server with the **PostGIS** extension enabled. Missing these produces load-time/connection errors, not application bugs.

Connection details are read from environment variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) with local defaults, so no credentials are committed. One-time setup on the server: create the database, run `CREATE EXTENSION postgis;`, then `python manage.py migrate`. The `psycopg2-binary` driver is pinned in `requirements.txt`.

## Data model architecture

All domain logic lives in `inventory/models.py`. It centers on four core entities and joins them with **explicit junction models that carry their own attributes** (do not treat these as plain `ManyToManyField`s):

- **Core**: `Bell` (Klok), `Founder` (Gieter), `Tower` (Toren), `Carillon` (Beiaard). A `Carillon` belongs to a `Tower` via FK.
- **Junctions** (each `unique_together` on its two FKs, each with dates/flags/comments):
  - `Bell_Tower` — a bell's placement in a tower over time (`is_current_location`, start/end dates).
  - `Carillon_Bell` — a bell's membership in a carillon (`relative_pitch`).
  - `Bell_Founder` — who cast/worked a bell (`is_primary_founder`, `type_of_work`).
- **`File`** — an uploaded asset (image/pdf/csv, extension-validated) with nullable FKs to any of Bell/Carillon/Founder/Tower, so one file can attach to whichever entity applies.

Conventions to follow when extending models:
- Nearly every field is `blank=True, null=True` — records are expected to be partial while research is ongoing.
- Every model sets a Dutch `verbose_name` / `verbose_name_plural`; match this when adding fields or models.
- `IntegerField` years use `MinValueValidator(600), MaxValueValidator(2100)`; reuse this range for date-of-casting fields.
- `Tower.save()` auto-composes `full_address` from the structured address parts — set those parts, not `full_address` directly.
- All models are registered in `inventory/admin.py` (bulk `register`, no custom `ModelAdmin` yet); register new models there.

## Views, URLs, templates

`inventory/views.py` currently contains function-based stubs that only `render()` a template with no context — none are wired to the models yet. URLs are declared in `campanarium/urls.py` (project-level, not an app `urls.py`). Templates in `inventory/templates/` extend `base.html`, which uses Bootstrap 4 via CDN. When implementing a page, this is where model data needs to be threaded through.

## README vs. reality

The `README.md` describes older aspirational tech (MySQL, Vue.js, REST API endpoints). The actual stack is **PostgreSQL + PostGIS** with server-rendered Django templates and no API layer. MySQL and Vue.js are not used — trust the code and this file over the README for stack decisions.
