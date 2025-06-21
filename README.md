# Arches RBAC Permissions

### Functionality

Currently within this repository:

 - datatypes for users and (Django) groups
 - Person, Group, Set and LogicalSet types (based on [Arches for Science](https://github.com/archesproject/arches-for-science/))
 - permissions based on relationships between those
 - caching of resource permissions without Django Guardian
 - nested permissions (hierarchies)
 - permissions based on Arches searches
 - management of people and roles through the Arches front-end
 - (to add) Group Manager for visualizing organograms from Coral project
 - (to add) flows for user sign-up, auto-permissioning and attaching to Person from Coral project

TODO: finish out and tidy

### Suggested Plan

An outcome of the [Arches Developer Meeetup 2025](https://flaxandteal.github.io/arches2025-website/) was that we want

 - tidy up this repository (linting, full types)
 - add (in-process) tests
 - make casbin optional and update naming to decouple
 - make worker/rabbit optional
 - split into in-Arches user management and permissions Arches Applications (likely to be a dependency relationship)
 - upstream plan agreement and light review (**external dependency**)
 - tidy up and add the views/templates for user management from coral-arches
 - temporarily add our custom dependencies (AORM, Arches F&amp;T fork)
 - rebase our critical Arches changes (flaxandteal/arches#docker-7.6) to Arches itself and investigate upstreaming (or changing functionality here instead)
 - look at whether we can move from AORM to QuerySets, at least in part
 - integrate/rebase onto Farallon's Default Deny
 - finalize merging of plugins (**external dependency**)

#### Future

Make a more straightforward way to build logical sets, other than copying search URLs.
Nodegroup permissions in the same approach as resource permissions. This would be easiest with a PG/ES tile index as an alternative to resource indexing.

### Installation

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

### Acknowledgements

Much of this development was undertaken during the period of a project for
the NI [Historic Environment Division](https://www.communities-ni.gov.uk/topics/historic-environment), who provided valuable insights and
feedback to functionality, as well as to [Junaid Abdul Jabbar](https://www.arch.cam.ac.uk/staff/junaid-abdul-jabbar)
for input and testing in collaboration.

The base of this Arches Application is from [@chiatt](github.com/chiatt)'s Arches Dashboard example project.

Thanks are due to the Arches Core team at [Farallon](https://www.fargeo.com/) and [GCI](https://www.getty.edu/conservation/)
for the fantastic Arches project.

A number of ancillary files, including linting, doc generation and CI,
were taking from the Apache2-licensed [DeWReT](https://github.com/flaxandteal/dewret) library.

With thanks to the kind support of [GCI](https://www.getty.edu/conservation/) and other contributors in helping
to progress this work for wider reusability.
