from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import login, logout
from rest_app.config.supabase_config import supabase_client
from rest_app.models import Account
from rest_app.services.auth_service import SupabaseAuthService

import logging


logger = logging.getLogger(__name__)

class SupabaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require authentication
        self.public_paths = ['/login/', '/register/']
        
    def __call__(self, request):
        # Don't check authentication for public paths
        if request.path.startswith('/admin'):
            return redirect(settings.LOGOUT_REDIRECT_URL)

        if any(request.path.startswith(path) for path in self.public_paths) or request.path == "/":
            return self.get_response(request)
        
        # Check if user is authenticated with a valid Supabase token
        is_valid = SupabaseAuthService._validate_token(request)
        if not is_valid:
            SupabaseAuthService.sign_out(request)
            # Logout user and redirect to login page
            return redirect(settings.LOGIN_URL)
            
        # Process the request and return the response
        response = self.get_response(request)
        return response