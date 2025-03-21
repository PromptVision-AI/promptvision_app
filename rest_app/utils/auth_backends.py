from django.contrib.auth.backends import ModelBackend
from rest_app.models import Account

# In Django, authentication backends are classes that implement two key methods:
# authenticate() - Attempts to verify credentials and return a user object
# get_user() - Retrieves a user by ID from the session data
# These backends are used by Django's authenticate() and login() functions to verify credentials and persist user sessions.

class SupabaseAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        This method is not actually used for authentication.
        Authentication is handled by the SupabaseAuthService.
        This is just here to conform to Django's auth system.
        """
        return None
        
    def get_user(self, user_id):
        """
        Get a user by their ID (used by session authentication)
        """
        try:
            return Account.objects.get(pk=user_id)
        except Account.DoesNotExist:
            return None 