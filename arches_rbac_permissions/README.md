# Arches RBAC Permissions

### Functionality

Currently within this repository:

 - datatypes for users and (Django) groups
 - Person, Group, Set and LogicalSet types (based on [Arches for Science](https://github.com/archesproject/arches-for-science/))
 - permissions based on relationships between those
 - caching of resource permissions without Django Guardian
 - nested permissions (hierarchies)
 - permissions based on Arches searches
 - partial management of people and roles through the Arches front-end (not a full replacement for superuser user/password management)
 - flows for user sign-up, auto-permissioning and attaching to Person
 - (to fix) Group Manager for visualizing organograms from Coral project

TODO: finish out and tidy

### Suggested Plan

An outcome of the [Arches Developer Meeetup 2025](https://flaxandteal.github.io/arches2025-website/) was that we want

 - tidy up this repository (linting, full types)
 - add (in-process) tests
 - make casbin optional and update naming to decouple
 - ~~make worker/rabbit optional~~
 - ~~split into in-Arches user management and permissions Arches Applications (likely to be a dependency relationship)~~
 - upstream plan agreement and light review (**external dependency**)
 - ~~tidy up and add the views/templates for user management from coral-arches~~
 - ~~temporarily add our custom dependencies (AORM, Arches F&amp;T fork)~~
 - ~~rebase our critical Arches changes (flaxandteal/arches#docker-7.6) to Arches itself and investigate upstreaming (or changing functionality here instead)~~
 - look at whether we can move from AORM to QuerySets, at least in part
 - ~~integrate/rebase onto Farallon's Default Deny~~
 - finalize merging of plugins (**external dependency**)

This plan changed in July 2025, on request, to:

  - ensure the repository is compatible with Arches 8
  - it can be run and used (mostly) normally

before progressing. Having made that up-front investment, we plan to tidy this for upgrading our
existing and new customers to Arches 8 long term. As such, especially keen to collaborate
on approaches that align with project-wide goals to reduce later work across the community.

**Alpha-testers wanted - please reach out to admin@flaxandteal.co.uk**

#### Structure

The repo is split into five Applications, one of which is simply a convenience wrapper.

 - arches_rbac_permissions: proxy for the other three
 - arches_user_datatype: widgets and datatypes for Django Users and Django Groups, with a (configurable) sign-up workflow
 - arches_inclusion_rule: widget and datatype for saved rules, currently only for ES-defined rules, but stubs for Querysets
 - arches_saved_search: (temporary) a mock-up-level Application for saving a search that can later be re-shown
 - arches_semantic_roles: Person, Group, Logical Set and Set models that use the above

#### Known Issues

 - Docs and linting: major changes are still expected structurally, so feedback would be helpful first!
 - Limited tests: given the expected changes, the first question is whether the end-to-end works predictably, but automated testing is the next highest priority
 - Casbin is still present - discussion to be had
 - Elasticsearch is still a dependency, but now SearchRules are abstracted in the hope that they can be defined in multiple ways (and persisted in the incoming `sets` table regardless of how they are defined)
 - Group Manager depended on the relationship ontology classes, but this forces an ontology, which is undesirable, so right now it is pretty broken
 - Person is still a standalone model, instead of a reusable branch
 - It uses Knockout: unfortunately, Widgets that work in Knockout must be Vue-less (so these will need rewritten, and are consequently rougher)

Several issues appear to be side-effects of the move to Arches 8, and off a fork, and as such are hopefully resolvable:

 - Term search: this bypasses resource-wise permissions, including ours
 - AORM/Arches8 compatibility: it should be possible to remove the dependency on AORM entirely, as everything could be done with Querysets (help welcome)
 - Deep linking into the request: core database search plugins access the request object, for the user and querystring, which currently requires brittle workarounds
 - Casbin startup: Django discourages DB access at startup, so there is a workaround to force Casbin to load slightly later
 - Performance: this was previously very fast (&lt;1min rebuild for ~20 hierarchical groups accessing 60k records), but hooking into the plugin structure may miss some of the optimizations we used
 - No resource_indexed signal: this was made private, but perhaps could be made public again? This allows us to re-run rules only against the saved record

Several issues are new as a result of moving to several standalone Applications:

 - Installation steps: it would be good to merge steps where possible, and remove `uv`
 - No guaranteed Celery: without Celery, we need to do rebuilds in-process and they are be triggered by saves. However, this is probably far more frequent than necessary; currently a simple debounce is used to limit the re-runs.

The Celery version is currently not ported from 7.6, but this will be need to be re-enabled before we can upgrade our own instances, so soon.

#### Future

Nodegroup permissions in the same approach as resource permissions. This would be easiest with a PG/ES tile index as an alternative to resource indexing.

Having a Postgres-only option - this assumes a general search query can be parsed into Querysets.

Our goal is to allow Postgres-only operation, using Querysets.

### Installation

Arches RBAC Permissions... (thanks to Cyrus for the base text from the Dashboard example).

__These instructions are currently removed to avoid ambiguity while testing - follow the steps below.__

1. ~~Install if from this repo (or clone this repo and pip install it locally).~~

2. ~~Install the arches querysets (or clone this repo and pip install locally).~~

3. Add `"arches_rbac_permissions"`, `"arches_querysets"` and `"casbin_adapter.apps.CasbinAdapterConfig"` to the INSTALLED_APPS setting in the project's settings.py file.

FIXME: TBC = To be confirmed? As in we are not sure if this is necessary? Is there not a better way than importing all (*) here?
#TBC
Ensure the Application settings are available to extend with:
```
from arches_rbac_permissions.settings import *
```
after `from arches.settings import *`.

FIXME: Above we are instructed to edit the INSTALLED_APPS setting (which is a tuple for some reason). Here we are instructed to add list by the same name? I am confused.
Make the following addition:
```
INSTALLED_APPS = [
    ...
    *ARCHES_RBAC_PERMISSIONS_APPS,
]
```

FIXME: But this is the first occurance of "MIDDLEWARE", and should result in a NameError.
Correct `MIDDLEWARE = [...` to `MIDDLEWARE += [...`

4. Version your dependency on `"arches_rbac_permissions"` and `"arches_querysets"` in `pyproject.toml`:
```
dependencies = [
    "arches>=7.6.0,<7.7.0",
    "arches_rbac_permissions==0.0.1",
    "arches_querysets[drf]"
]
```

5. Add the application to your URLs in `urls.py`:
```
urlpatterns.append(path('', include('arches_rbac_permissions.urls')))
urlpatterns.append(path("", include("arches_querysets.urls")))
```

6. Add `cytoscape-elk` to your npm dependencies:
```
npm i --save cytoscape-elk
```

7. From your project run migrate to add the model included in the app:
```
python manage.py migrate
```

8. Next be sure to rebuild your project's frontend to include the plugin:
```
npm run build_development
```

### Development set up

The following steps should get you set up for development with `arches-rbac-permissions`.
The approach involves running `elasticsearch` and `postgis` in Docker containers, but you should have other [Arches dependencies](https://arches.readthedocs.io/en/stable/installing/requirements-and-dependencies/) as well clang installed.

1. Create a project folder and environments
    ```shell
    mkdir rbac-test
    cd rbac-test
    ```

    ```shell
    python -m venv .venv
    . .venv/bin/activate

    pip install nodeenv
    nodeenv -n 20.18.2 .nenv
    . .nenv/bin/activate
    ```

2. Clone arches and start a project
    ```shell
    git clone https://github.com/archesproject/arches
    cd arches
    git checkout dev/8.1.x # a6d1eb
    pip install -e .
    cd ..

    arches-admin startproject rbac_test_prj
    ```
    This should make a sample project directory directory `rbac-test-prj` (with dashes) containing in particular a `pyproject.toml` file, a `rbac_test_prj/settings.py` file, and a `rbac_test_prj/urls.py` file that you will edit in step 7 below.

    FIXME: What is the following parenthetical expressing? Ignoring
    (cd arches && pip install -e .)

3. Add rbac-permissions

    ```shell
    git clone https://github.com/flaxandteal/arches-rbac-permissions
    pip install uv # Currently needed for monorepo (dev only)
    cd arches-rbac-permissions/arches_rbac_permissions
    uv pip install -e . # Note the uv prefix
    cd .. # FIXME: confirm this is cd up one level and not two (ie back to rbac-test/arches-rbac-permissions/ or rbac-test/ )
    ```

    FIXME: What is the following parenthetical expressing? Only going up one level means `arches/` is not a subdir. Ignore.
    (cd arches && pip install -e .) # It is still marked as an alpha

4. Add query sets
    ```shell
    git clone https://github.com/archesproject/arches-querysets.git
    cd arches-querysets
    pip install -e .
    cd ..
    ```

5. Start elastic search

    In another shell
    ```shell
    docker run --rm --name some-es -e "discovery.type=single-node" -p9200:9200 -e POSTGRES_PASSWORD=postgis elastic/elasticsearch:7.17.27
    ```

6. Start postgis

    In another shell
    ```shell
    docker run --rm --name some-postgres -p5432:5432 -e POSTGRES_PASSWORD=postgis postgis/postgis
    ```

7. Edit test project settings
    ```shell
    cd ../rbac-test-prj
    ```
    - Following [Installation](#installation) step 4 edit the `pyproject.toml` file
    - Following [Installation](#installation) step 5 edit the `rbac_test_prj/urls.py` file
    - Following [Installation](#installation) step 3 edit the `rbac_test_prj/settings.py` file. 
    There are three changes concerning:
        - import statement
        - INSTALLED_APPS
        - MIDDLEWARE

    In addition to edits for step 3 made above, in `rbac_test_prj/settings.py` make the following changes:
    - Add an elasticsearch host
    ```python
    ELASTICSEARCH_HOSTS = [{"scheme": "http", "host": os.environ.get("ESHOST", "localhost"), "port": int(os.environ.get("ESPORT", 9200))}]
    ```
    - Uncomment the dummy email backend
    ```python
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    ```

8. Do something with the local wildlife

    ```shell
    npm i --save cytoscape-elk
    ```
    and reset / setup the database
    ```shell
    python manage.py setup_db # confirm DB reset
    ```
    Note that setup_db **cannot** be run twice - known (new) bug

    Finally make some directories
    ```shell
    mkdir -p rbac_test_prj/{media/js,templates}/views/components/widgets
    ``` 
    TODO: Resolve if this is actually needed.

9. Load arches packages
    TODO: Figure out how to run these as a group
    ```shell
    python manage.py packages -o load_package -a arches_user_datatype
    python manage.py packages -o load_package -a arches_inclusion_rule
    python manage.py packages -o load_package -a arches_semantic_roles #FIXME: Errors
    ``` 

    Note: The following may be necessary if there are npm errors:
    ```shell 
    cp ../arches/webpack/webpack-utils/build-filepath-lookup.js webpack/webpack-utils/build-filepath-lookup.js
    ``` 

    ```shell 
    python manage.py packages -o load_package -s ../arches-rbac-permissions/tests/example/ #FIXME: Errors
    ``` 

10. Lastly spin up arches
    ```shell
    npm run build_development
    python manage.py runserver
    ```

    At this point, a regular Arches instance with admin login should be available on localhost:8000

Cleanup: to deactivate your development environment: 
```shell
deactivate_node # close node js nenv
deactivate  # close python venv
```

### Example

The example package shows a book management database. Log in as admin and [search for Books](http://localhost:8000/search?paging-filter=1&tiles=true&format=tilecsv&reportlink=false&precision=6&total=14&exportsystemvalues=false&resource-type-filter=%5B%7B%22graphid%22%3A%22717291c0-99cc-4aa0-98c1-b37cc21a8a3a%22%2C%22name%22%3A%22Book%22%2C%22inverted%22%3Afalse%7D%5D). Several of these books are by the authors Steven Erikson and Ian C. Esslemont, and one is by Ian McDonald.

#### Malazan

Assets:

| Graph          | Resource                   |
|----------------|----------------------------|
| Book           | Toll the Hounds            |
| Book           | Deadhouse Gates            |
| Book           | Dancer's Lament            |
| Person         | Steven Erikson             |
| Person         | Ian C. Esslemont           |
| Group          | Malazan Authors            |
| Set            | Malazan Empire Franchise   |
| Set            | Malazan Book of the Fallen |

Two first two books are by Steven Erikson and are part of the Malazan Book of the Fallen. The third books is part of the same franchise, but is by Ian C. Esslemont.

#### Ian McDonald

| Graph          | Resource                   |
|----------------|----------------------------|
| Book           | River of Gods              |
| Person         | Ian McDonald               |
| Group          | Ian McDonald's Team        |
| Logical Set    | Works by Ian McDonald      |

Ian McDonald is the author of River of Gods. Here, he is the only member of his team, a group that has access to all of his works.

### Exercises

#### Attaching a user to a person

[Edit Ian McDonald](http://localhost:8000/resource/44dd85c1-0132-44e3-b248-50f6b6d6f3d2) and go to the `User Account` option. Like any other system or external reference, this may or may not be populated depending on the referent's presence in the other system - in this case the user table.

The user widget can be placed anywhere. Currently, it carries meaning because the Person model is part of this Application, but this will likely be replaced with node configuration, such that it can be a human-person link on any model.

There should be an option to "Copy signup link". Click it.

In a new _private_ browser window, paste from your clipboard. If you did not configure the dummy email server above, do so now and restart the server.

Enter a chosen username (e.g. `ianm`), email (e.g. `ianm@example.com`) and password (e.g. `Pass1234$`).

When you submit, you should see an email in your log window with a URL. Copy this. It will look something like (but different to):

               <p><a href="http://localhost:8000/person-confirm-signup?link=uaWIU1ns7uQXDBNFXCo2U6KZ%2FEj7LgV0qIG8cgwNIPTmxjPnyy5xOLFm3xbrgUH0uoshWGbOV3OU8AK8ieXIMPW1ZgcEXr4jwFI12FdOHyJBSZCFo2c756xppZiQpeHsW9T%2BIgjcTgPdFZ%2FTApiafH8JSLq45Y3%2F7uN4klNEDfgH%2Fu9UF3AeBAHXJ6XGHzmcai6hmZg%2BR67%2F1JWXaaHdsmsZuduKWAEFMdxUUdYnQTNQL%2FSi7HNJaNvDKtIg0onV8CbC7J2TtcT54GlZ0TVvY7ZjGkzF2OcLvon2Hu9lk42Xpty4%2BbbI5fvGf3GE3yDRDLPExce7VGOLxBRDh9JMKYjMPCYS2SMT6Xs5s5ZjJ7hsVAxSSOOQiwxeOa8uP7wW">Signup for Arches</a></p>

Copy and paste it to your _private_ browsing window. It should confirm your account is now active.

When you sign in, you should have an unprivileged account. Return [to search](http://localhost:8000/search?paging-filter=1&tiles=true). You should see one book, `River of Gods`.

#### Creating a Logical Set

Complete the task above. Return to the admin user and go to Search.

From the Advanced Search, pick Person &rarr; Names and set the value to `Ian`. You should see two entries, Ian C. Esslemont and Ian McDonald. Set the Lifecycle State to `Active (Standard)`. You should see no entries.

Click the Bookmark icon - third from right, under the logout button. Enter the text "Active People with IAN in their name" into `Enter name for search` and click Save. You should see a message "Saved".

Create a new resource - a Logical Set - from the Add New Resource toolbar menu. Make the Title, "Ians" and when you go to Member Definition, you should see an option to "Copy from your saved search: Active People with IAN in their name". On selecting this, you will see a warning that your search, in becoming an inclusion rule, will be visible to other users of the Logical Set. Click OK, then Add.

Edit the [Ian McDonald's Team](http://localhost:8000/resource/eba96b33-603b-4c4e-aaba-8e964a3b6d57) group, and add a new Permission: to Object `Ians`, with Action `Reading`.

If you return to the unprivileged user (Ian McDonald) in your private browsing, then you should see no change. Only the `River of Gods` is visible, unless you changed other permissions.

Back in the admin account, edit [Ian C. Esslemont](http://localhost:8000/resource/b647bd9a-15f9-48c6-800c-4496fd8269d6) and click `Make Active`. If you check your private browsing window, and update the search, perhaps by resorting, you should see Ian C. Esslemont appearing in the list. Do the same with [Ian McDonald](http://localhost:8000/resource/44dd85c1-0132-44e3-b248-50f6b6d6f3d2) himself. With ~5s, you should see his record has been added to the available items in his list.

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
