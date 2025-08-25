"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import time
import logging
import readline
import psycopg2
from django.core.management.base import BaseCommand

from arches_inclusion_rule.utils.es_set_applicator import SetApplicator

from arches.app.models.system_settings import settings

logging.basicConfig()

COOLOFF_S = 10

class Command(BaseCommand):
    """Recalculate ES resource->set mapping.

    """

    print_statistics = False

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--statistics",
            action="store_true",
            dest="print_statistics",
            help="Do extra searches to provide relevant statistics?",
        )

        parser.add_argument(
            "-S",
            "--synchronous",
            action="store_true",
            dest="synchronous",
            help="Run update-by-query synchronously",
        )


    def handle(self, *args, **options):
        print_statistics = True if options["print_statistics"] else False
        synchronous = True if options["synchronous"] else False

        set_applicator = SetApplicator(print_statistics=print_statistics, wait_for_completion=True, synchronous=synchronous)
        try:
            set_applicator.apply_sets()
        except psycopg2.OperationalError:
            time.sleep(COOLOFF_S)

        try:
            # Cannot be imported until Django ready
            from arches_semantic_roles.permissions.casbin import CasbinPermissionFramework
            framework = CasbinPermissionFramework()
            framework.recalculate_table()
        except ImportError:
            # TODO: Find a nicer way of making this standalone without the obvious footgun
            # of updating the sets and not updating the permissions that depend on them.
            ...
