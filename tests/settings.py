"""Django settings for importing and unit-testing the RBAC suite.

This mirrors what a host Arches project does (see the README "Installation"
steps): load the suite settings, then register the bundled apps in
``INSTALLED_APPS``. That is enough to import the apps' modules and exercise their
pure logic. No live database, Elasticsearch or Casbin runtime is required for the
unit tests under ``tests/unit`` — they never use the ``db`` fixture, so
pytest-django does not stand up a database.
"""

from arches_rbac_permissions.settings import *  # noqa: F401,F403

# Append the suite's apps without introducing duplicate app labels.
_installed = list(INSTALLED_APPS)  # noqa: F405
for _app in ARCHES_RBAC_PERMISSIONS_APPS:  # noqa: F405
    if _app not in _installed:
        _installed.append(_app)
INSTALLED_APPS = _installed
