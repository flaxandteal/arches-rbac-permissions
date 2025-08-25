import json
from django.db.models import Q
from django.contrib.auth.models import User
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.views.base import BaseManagerView
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.response import JSONResponse

def user_to_string(user: User) -> str:
    return f"{user.email} (user.username)" if user.email else user.username

def paged_user_list(request):
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
        results = User.objects.filter(
            Q(username__contains=query) |
            Q(first_name__contains=query) |
            Q(last_name__contains=query) |
            Q(email__contains=query)
        )[
            offset:offset+limit
        ]
        total_count = len(results)
        data = [
            {
                "id": d.id,
                "text": user_to_string(d)
            } for d in results
        ]

        return JSONResponse({"results": data, "more": offset + limit < total_count})
    return JSONResponse({"status": "error", "message": "Not authorized"}, status=403)

def user_get(request):
    if request.user and (
        # TODO: higher permission
        user_is_resource_reviewer(request.user) or
        request.user.is_superuser
    ):
        try:
            userid = int(request.GET.get("userid", ""))
        except ValueError:
            return JSONResponse({"status": "error", "message": "User ID must be integer"}, status=401)

        user = User.objects.get(id=userid)

        return JSONResponse({"id": userid, "text": user_to_string(user)})
    return JSONResponse({"status": "error", "message": "Not authorized"}, status=403)
