from typing import Literal
from contextvars import ContextVar
from contextlib import contextmanager
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User

current_user: ContextVar[User | None] = ContextVar('current_user', default=None)

def get_current_user() -> User | None | Literal[False]:
    """
    If a user is logged in and set in this Python context, return them,
    otherwise return None.
    :return: User if logged in, None if set to None and False if unset at all
    """
    try:
        user: User | None = current_user.get()
    except LookupError:
        user = False
    return user

@contextmanager
def set_current_user(user: User | None):
    try:
        token = current_user.set(user)
        yield
    finally:
        current_user.reset(token)

class CurrentUserMiddleware(MiddlewareMixin):
    """
    Without passing the user to places that should
    not see the request object, or customizing Arches internals,
    this seems the only clean remaining option (and is a specific
    intended use-case for ContextVars in PSL).

    In the F+T patch, we make the user available without request,
    which makes it easier to pass.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with set_current_user(request.user):
            response = self.get_response(request)
        return response
