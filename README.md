# Arches RBAC Permissions

Arches Permissions... (thanks to Cyrus for the base text from the Dashboard example).

You can add the dashboard to an Arches project in just a few easy steps.

1. Install if from this repo (or clone this repo and pip install it locally). 
```
pip install git+https://github.com/flaxandteal/arches-rbac-permissions.git
```

2. Add `"rbac_permissions"` to the INSTALLED_APPS setting in the demo project's settings.py file below the demo project:
```
INSTALLED_APPS = [
    ...
    "demo",
    "rbac_permissions",
]
```

3. Version your dependency on `"rbac_permissions"` in `pyproject.toml`:
```
dependencies = [
    "arches>=7.6.0,<7.7.0",
    "rbac_permissions==0.0.1",
]
```

4. From your project run migrate to add the model included in the app:
```
python manage.py migrate
```

5. Next be sure to rebuild your project's frontend to include the plugin:
```
npm run build_development
```

# Acknowledgements

Much of this development was undertaken during the period of a project for
the NI Historic Environment Division, who provided valuable insights and
feedback to functionality.

A number of ancillary files, including linting, doc generation and CI,
were taking from the Apache2-licensed [DeWReT](https://github.com/flaxandteal/dewret) library.
