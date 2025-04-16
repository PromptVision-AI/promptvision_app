from django.shortcuts import redirect
from django.conf import settings

def custom_page_not_found_view(request, exception):
    # If not authenticated, redirect to login
    if not request.session.get("user_id"):
        return redirect(settings.LOGIN_URL)
    # If authenticated, redirect to conversation list
    return redirect(settings.LOGIN_REDIRECT_URL)