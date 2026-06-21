# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A relationship-based access control (RBAC) suite for [Arches](https://archesproject.org/),
delivered as five separate **Arches Applications** managed in one `uv` workspace monorepo.
It is **Alpha** and targets **Arches 8.1** (`arches>=8.1,<8.2`, currently resolves to 8.1.2,
with `arches_querysets>=1.1,<1.2`), Python 3.11/3.12. Expect
structural churn — the README's "Known Issues" / "Suggested Plan" sections are the canonical
roadmap and are frequently more current than the code.

Each top-level `arches_*/` directory is an independently-packaged app (hatchling build,
its own `pyproject.toml`, `settings.py`, `apps.py`, `urls.py`, and a nested
`arches_<name>/arches_<name>/` Python package). The five apps:

- **`arches_rbac_permissions`** — convenience meta-package. No logic of its own: its
  `settings.py`, `urls.py` just splice together the other four (`ARCHES_RBAC_PERMISSIONS_APPS`).
  This is the single dependency consumers install.
- **`arches_semantic_roles`** — the core. Person/Group/Set/Logical Set resource models and the
  Casbin-based permission framework that derives resource permissions from relationships between them.
- **`arches_inclusion_rule`** — datatype + rules for defining set membership. Currently
  Elasticsearch-search-backed (`SearchRule`); `QuerySetRule` is a stub for a future Postgres-only path.
- **`arches_user_datatype`** — widgets/datatypes linking Arches resources to Django `User` and
  `Group`, plus a configurable sign-up / auto-permissioning workflow.
- **`arches_saved_search`** — temporary mock-up app for persisting a search to re-show later
  (used to seed an inclusion rule from a saved search).

`main.py` and the root `__init__.py` are vestigial stubs, not entry points.

## How permissions actually work (the big picture)

1. Resource models **Person, Group, Set, Logical Set** (graph IDs in
   `arches_semantic_roles/.../wkrm.toml`, root group IDs in `settings.GROUPINGS`) express access
   relationships. Logical Sets carry an **inclusion rule**; plain Sets list members explicitly.
2. **Set membership** is materialised into Elasticsearch: `SetApplicator`
   (`arches_inclusion_rule/.../utils/es_set_applicator.py`) runs each rule's query and writes a
   `sets` array onto each resource's ES document via update-by-query.
3. **Casbin** turns groups + set memberships into a policy table.
   `CasbinPolicyBuilder` (`arches_semantic_roles/.../permissions/casbin_policy_builder.py`)
   orchestrates the per-source **processors** (`permissions/processors/`:
   `DjangoGroupProcessor`, `ArchesGroupProcessor`, `SetProcessor`, …). The Casbin model is
   `permissions/casbin.conf` (RBAC with `g`/`g2` grouping over subjects and objects). The
   framework integrating with Arches is `permissions/casbin.py` (`CasbinPermissionFramework`,
   wired via `PERMISSION_FRAMEWORK` and `dauthz.backends.CasbinBackend`).
4. **Recalculation is signal-driven and debounced.** `arches_semantic_roles/.../service.py`
   listens on Django `post_save`; saving a Person/Group/Set/Logical Set trips a debounced timer
   (`CASBIN_TRIGGER_DEBOUNCE_SECONDS`, default 5s) that re-applies sets and/or reloads the Casbin
   policy **in-process** (`CasbinInProcessTrigger`). A RabbitMQ/`pika`-based multi-process
   `CasbinTrigger` exists but is gated off by `ENABLE_CASBIN_TRIGGER` (currently `False`); Celery
   is not yet ported from the 7.6 version. The old `resource_indexed` signal hook is commented
   out (signal was made private upstream) — this is why recalculation is broader/more frequent
   than ideal.

Cross-app coupling lives in `settings.py` files: apps additively extend Arches settings lists
(`DATATYPE_LOCATIONS`, `RULE_LOCATIONS`, `PERMISSION_LOCATIONS`, `MIDDLEWARE`,
`WELL_KNOWN_RESOURCE_MODELS`, `ARCHES_RBAC_PERMISSIONS_APPS`). `SEARCH_BACKEND` is overridden to
`arches_inclusion_rule.utils.search.UpdatingSearchEngine`.

### Notable constraints / gotchas
- Depends on **`arches_orm` (AORM)** and **`arches_querysets`**; an explicit goal is to migrate
  AORM usage to Django QuerySets toward a Postgres-only option.
- DB access at app startup is discouraged by Django, so `apps.py` patches
  `CasbinAdapterConfig.ready` to a no-op and defers enforcer init.
- **Knockout, not Vue**: front-end widgets live under each app's `media/js/` and `pkg/extensions/`
  and must be Vue-less to work with Knockout.
- Permission/datatype/casbin modules frequently can only be imported *after* Django is ready —
  hence the many function-local imports; preserve that pattern.

## Commands

This is a `uv` workspace. Develop against a live Arches checkout (see the long, authoritative
**Development set up** in `arches_rbac_permissions/README.md` — Arches `dev/8.1.x`, Postgres+ES in
Docker, a nodeenv, then `uv pip install -e .` per app).

```bash
# Lint / format (ruff; config in arches_rbac_permissions/pyproject.toml — selects D,F,B, google docstrings)
ruff check .
ruff format .

# Types (strict)
mypy --strict --install-types --allow-subclassing-any --non-interactive <path>

# Pre-commit: runs ruff, ruff-format, mypy, and conventional-commit message check
pre-commit install --hook-type commit-msg
pre-commit run --all-files
```

**Commit messages must be Conventional Commits** (`feat:`, `fix:`, `chore:`, …) — enforced by
the `commit-msg` hook and visible in git history.

Management commands (run via the host Arches project's `manage.py`):
```bash
python manage.py apply_sets [-s] [-S]      # recalc ES resource→set mapping (+ Casbin table)
python manage.py print_permissions_table   # debug: dump derived permissions
python manage.py export_rbac
```

Load the demo "book management" package (Malazan / Ian McDonald example) for manual testing:
```bash
python manage.py packages -o load_package -a arches_user_datatype
python manage.py packages -o load_package -a arches_inclusion_rule
python manage.py packages -o load_package -a arches_semantic_roles
python manage.py packages -o load_package -s ./tests/example/
```

### Tests
```bash
uv sync --group dev      # first time: installs pytest + pytest-django
uv run pytest            # runs tests/unit (config in root pyproject [tool.pytest.ini_options])
```
`tests/unit/` holds the in-process unit suite. It runs under `tests/settings.py`, a settings
module that mirrors a host project (`from arches_rbac_permissions.settings import *` then registers
`ARCHES_RBAC_PERMISSIONS_APPS` in `INSTALLED_APPS`) so the apps import via `django.setup()`. These
tests exercise **pure logic only** and never use the `db` fixture, so pytest-django does not stand
up Postgres/Elasticsearch. Importing Arches still needs the **GDAL** system library present.

Anything touching the database, Elasticsearch, Casbin enforcement, or AORM's dynamically-generated
models (e.g. `from arches_orm.models import Group`) needs the full dev runtime from the README and
does **not** belong in `tests/unit`. `tests/example/` is the demo package's fixture data, not tests.

**CI caveat:** the GitHub Actions workflows (`.github/workflows/python-*-ci.yml`) are inherited
DeWReT boilerplate — they reference a non-existent `./src` tree, `dewret`, and an `example/` dir, so
they do **not** run this suite. They need rewriting to `uv run pytest`; don't trust green CI yet.
