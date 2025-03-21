from functools import wraps
from django.shortcuts import redirect
from django.conf import settings

def public_only(view_func):
    """
    Decorator for views that should only be accessible to non-authenticated users.
    Redirects to user home if the user is already authenticated.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get("user_id"):
            return redirect(settings.LOGIN_REDIRECT_URL)
        return view_func(request, *args, **kwargs)
    return _wrapped_view 