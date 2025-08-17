import json
from typing import Literal
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.shortcuts import redirect
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.views.base import BaseManagerView
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.response import JSONResponse
from arches_rbac_permissions.models import InclusionRule, SavedSearch

SEARCH_RULE_CLASS = ("search_rule", "SearchRule")

# TODO - presumably this can be done better with components
KNOWN_NON_SEARCH_COMPONENT_QUERY_FIELDS = {'tiles', 'total', 'format', 'precision', 'reportlink', 'paging-filter', 'exportsystemvalues'}

def saved_search_to_string(saved_search: SavedSearch) -> str:
    return f"{saved_search.name}"

def inclusion_rule_to_string(inclusion_rule: InclusionRule) -> str:
    return f"{inclusion_rule.name}"

def paged_inclusion_rule_list(request):
    if request.user:
        query = request.GET.get("query", "")
        only_keep_rule_ids: None | Literal[False] | list[str] = request.GET.getlist("onlyKeepRuleIds[]", False) or request.GET.get("onlyKeepRuleIds", False)
        print(only_keep_rule_ids)
        page = int(request.GET.get("page", 1))
        limit = 50
        offset = (page - 1) * limit

        # TODO: pagination by unioning

        # TODO: tie this down more
        data = []
        if only_keep_rule_ids != "":
            filter_query = Q(name__contains=query)
            if isinstance(only_keep_rule_ids, list):
                filter_query &= Q(pk__in=only_keep_rule_ids)
                print(only_keep_rule_ids)
            if not (
                # TODO: higher permission
                user_is_resource_reviewer(request.user) or
                request.user.is_superuser
            ):
                filter_query &= Q(owner=request.user)
            results = InclusionRule.objects.filter(filter_query)[
                offset:offset+limit
            ]
            data += [
                {
                    "id": str(d.inclusionruleid),
                    "isSavedSearch": False,
                    "canInspectRule": bool(d.get_search_rule_url()),
                    "text": inclusion_rule_to_string(d)
                } for d in results
            ]

        # TODO: does someone need to have savedsearch access for inclusion rules
        # if not even a resource reviewer?
        # TODO: tie this down more
        filter_query = Q(name__contains=query) & Q(user=request.user)
        results = SavedSearch.objects.filter(filter_query)[
            :(limit-len(data))
        ]
        # TODO: fix up pagination for >1pg saved search
        data += [
            {
                "id": "ss-" + str(d.savedsearchid),
                "isSavedSearch": True,
                "text": saved_search_to_string(d)
            } for d in results
        ]
        total_count = len(data)

        return JSONResponse({"results": data, "more": offset + limit < total_count})
    return JSONResponse({"status": "error", "message": "Not authorized"}, status=403)

def inclusion_rule_get(request):
    if request.user:
        try:
            inclusion_rule_id = request.GET.get("inclusionRuleId", "")
        except ValueError:
            return JSONResponse({"status": "error", "message": "User ID must be integer"}, status=401)

        io = InclusionRule.objects
        if not (
            # TODO: higher permission
            user_is_resource_reviewer(request.user) or
            request.user.is_superuser
        ):
            io = io.filter(owner=request.user)
        inclusion_rule = io.get(pk=inclusion_rule_id)

        return JSONResponse({
            "id": inclusion_rule_id,
            "isSavedSearch": False,
            "canInspectRule": bool(inclusion_rule.get_search_rule_url()),
            "text": inclusion_rule_to_string(inclusion_rule)
        })
    return JSONResponse({"status": "error", "message": "Not authorized"}, status=403)

def copy_inclusion_rule_from_saved_search(request):
    if request.user:
        try:
            saved_search_id = request.GET.get("savedSearchId", "")
        except ValueError:
            return JSONResponse({"status": "error", "message": "User ID must be integer"}, status=401)

        ss = SavedSearch.objects.filter(user=request.user, pk=saved_search_id).get()
        ir = InclusionRule()
        ir.name = ss.name
        ir.modulename, ir.classname = SEARCH_RULE_CLASS
        ir.definition = {k: json.loads(v) for k, v in ss.query.items() if k not in KNOWN_NON_SEARCH_COMPONENT_QUERY_FIELDS}
        ir.owner = request.user
        ir.save()

        return JSONResponse({
            "id": ir.pk,
            "isSavedSearch": False,
            "canInspectRule": bool(ir.get_search_rule_url()),
            "text": inclusion_rule_to_string(ir)
        })
    return JSONResponse({"status": "error", "message": "Not authorized"}, status=403)

def go_to_inclusion_rule_inspect(request):
    if request.user:
        try:
            inclusion_rule_id = request.GET.get("inclusionRuleId", "")
        except ValueError:
            return JSONResponse({"status": "error", "message": "User ID must be integer"}, status=401)

        io = InclusionRule.objects
        if not (
            # TODO: higher permission
            user_is_resource_reviewer(request.user) or
            request.user.is_superuser
        ):
            io = io.filter(owner=request.user)
        inclusion_rule = io.get(pk=inclusion_rule_id)

        if (get_inspect_url := inclusion_rule.get_search_rule_url()):
            return redirect(get_inspect_url)

        raise HttpResponseBadRequest("Cannot inspect this rule")
    raise PermissionDenied()
