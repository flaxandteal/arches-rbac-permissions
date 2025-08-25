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

import logging
import json
from django.views.generic import View
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches_saved_search.models import SavedSearch


logger = logging.getLogger(__name__)

class SavedSearchesView(View):
    def post(
        self,
        request,
    ):
        # TODO validation, etc. - but this (saved searches) is a temporary plugin for a better
        # one being written elsewhere
        if not request.user or not request.user.id:
            return JSONErrorResponse({"message": "No user"}, status=400)
        print(request.POST)
        saved_search = SavedSearch(
            user=request.user,
            query=json.loads(request.POST.get("query")),
            name=request.POST.get("savedSearchName"),
        )
        saved_search.save()
        return JSONResponse({
            "message": "Saved" # TODO: translation
        })

    def get(
        self,
        request,
    ):
        if not request.user or not request.user.id:
            return JSONResponse([])
        saved_searches = SavedSearch.objects.filter(
            user=request.user
        )
        return JSONResponse([
            {
                "name": saved_search.name,
                "query": saved_search.query
            } for saved_search in saved_searches
        ])
