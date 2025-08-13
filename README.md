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

2. Add `"arches_rbac_permissions"` to the INSTALLED_APPS setting in the demo project's settings.py file below the demo project.

#TBC
Ensure the Application settings are available to extend with:
```
from arches_rbac_permissions.settings import *
```

after `from arches.settings import *`

Make the following additions:
```
INSTALLED_APPS = [
    ...
    "arches_rbac_permissions",
    "arches_querysets",
    "casbin_adapter.apps.CasbinAdapterConfig",
    "demo",
]
```

Correct `MIDDLEWARE = [...` to `MIDDLEWARE += [...`

3. Version your dependency on `"arches_rbac_permissions"` in `pyproject.toml`:
```
dependencies = [
    "arches>=7.6.0,<7.7.0",
    "arches_rbac_permissions==0.0.1",
]
```

4. Add `cytoscape-elk` to your npm dependencies:
```
npm i --save cytoscape-elk
```

5. From your project run migrate to add the model included in the app:
```
python manage.py migrate
```

6. Next be sure to rebuild your project's frontend to include the plugin:
```
npm run build_development
```

### How this was tested

The environment was set up using:

    mkdir rbac-test
    cd rbac-test

    python -m venv .env
    . .env/bin/activate

    pip install nodeenv
    nodeenv -n 20.18.2 .nenv
    . .nenv/bin/activate

    git clone https://github.com/archesproject/arches
    cd arches
    git checkout dev/8.1.x # a6d1eb
    pip install -e .
    cd ..

    arches-admin startproject rbac_test

    (cd arches && pip install -e .)
    git clone https://github.com/archesproject/arches-rbac-permissions
    cd arches-rbac-permissions
    pip install -e .
    cd ..

    # In another window
    docker run --rm --name some-es -e "discovery.type=single-node" -p9200:9200 -e POSTGRES_PASSWORD=postgis elastic/elasticsearch:7.17.27
    # In another window
    docker run --rm --name some-postgres -p5432:5432 -e POSTGRES_PASSWORD=postgis postgis/postgis

    cd rbac-test
    # make the changes to pyproject.toml and settings.py
    # make the following adjustments for this test approach:
    # ELASTICSEARCH_HOSTS = [{"scheme": "http", "host": os.environ.get("ESHOST", "localhost"), "port": int(os.environ.get("ESPORT", 9200))}]
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  #<-- Only need to uncomment this for testing without an actual email server

    npm i --save cytoscape-elk
    python manage.py setup_db # confirm DB reset
    mkdir -p rbac_test2/{media/js,templates}/views/components/widgets # this seems like it should not be needed?
    python manage.py packages -o load_package -a arches_rbac_permissions

    # This may be necessary if there are npm errors:
    cp ../arches/webpack/webpack-utils/build-filepath-lookup.js webpack/webpack-utils/build-filepath-lookup.js

    python manage.py packages -o load_package -s ../arches-rbac-permissions/tests/example/

    npm run build_development
    python manage.py runserver

At this point, a regular Arches instance with admin login should be available on localhost:8000

### Example

The example package shows a book management database. Log in as admin and [search for Books](http://localhost:8000/search?paging-filter=1&tiles=true&format=tilecsv&reportlink=false&precision=6&total=14&exportsystemvalues=false&resource-type-filter=%5B%7B%22graphid%22%3A%22717291c0-99cc-4aa0-98c1-b37cc21a8a3a%22%2C%22name%22%3A%22Book%22%2C%22inverted%22%3Afalse%7D%5D). Several of these books are by the authors Steven Erikson and Ian C. Esslemont, and one is by Ian McDonald.

#### Malazan

+----------------+----------------------------+
| Graph          | Resource                   |
+----------------+----------------------------+
| Book           | Toll the Hounds            |
| Book           | Deadhouse Gates            |
| Book           | Dancer's Lament            |
| Person         | Steven Erikson             |
| Person         | Ian C. Esslemont           |
| Group          | Malazan Authors            |
| Set            | Malazan Empire Franchise   |
| Set            | Malazan Book of the Fallen |
+----------------+----------------------------+

Two first two books are by Steven Erikson and are part of the Malazan Book of the Fallen. The third books is part of the same franchise, but is by Ian C. Esslemont.

#### Ian McDonald

+----------------+----------------------------+
| Graph          | Resource                   |
+----------------+----------------------------+
| Book           | River of Gods              |
| Person         | Ian McDonald               |
| Group          | Ian McDonald's Team        |
| Logical Set    | Works by Ian McDonald      |
+----------------+----------------------------+

Ian McDonald is the author of River of Gods. Here, he is the only member of his team, a group that has access to all of his works.

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
