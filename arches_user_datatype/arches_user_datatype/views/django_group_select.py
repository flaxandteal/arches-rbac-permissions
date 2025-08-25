import json
from django.db.models import Q
from django.contrib.auth.models import Group as DjangoGroup
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.response import JSONResponse

def django_group_to_string(group: DjangoGroup) -> str:
    return group.name

def paged_django_group_list(request):
    if request.user and (
        # TODO: higher permission
        user_is_resource_reviewer(request.user) or
        request.user.is_superuser
    ):
        query = request.GET.get("query", "")
        page = int(request.GET.get("page", 1))
        limit = 50
        offset = (page - 1) * limit

        # TODO: tie this down more
        results = DjangoGroup.objects.filter(
            Q(name__contains=query)
        )[
            offset:offset+limit
        ]
        total_count = len(results)
        data = [
            {
                "id": d.id,
                "text": django_group_to_string(d)
            } for d in results
        ]

        return JSONResponse({"results": data, "more": offset + limit < total_count})
    return JSONResponse({"status": "error", "message": "Not authorized"}, status=403)

def django_group_get(request):
    if request.user and (
        # TODO: higher permission
        user_is_resource_reviewer(request.user) or
        request.user.is_superuser
    ):
        try:
            userid = int(request.GET.get("userid", ""))
        except ValueError:
            return JSONResponse({"status": "error", "message": "Django Group ID must be integer"}, status=401)

        user = DjangoGroup.objects.get(id=userid)

        return JSONResponse({"id": userid, "text": django_group_to_string(user)})
    return JSONResponse({"status": "error", "message": "Not authorized"}, status=403)
