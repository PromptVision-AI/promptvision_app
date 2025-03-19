from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

# Needs to be checked, whether it is used or not
class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Protected paths that require authentication
        self.protected_paths = ['/user-home/']
        
    def __call__(self, request):
        # Check if the path is protected and user is not authenticated
        if request.path in self.protected_paths and not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response 