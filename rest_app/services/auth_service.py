from django.conf import settings
from django.contrib.auth import get_user_model
from rest_app.config.supabase_config import supabase_client
import logging
import json

User = get_user_model()
logger = logging.getLogger(__name__)

class SupabaseAuthService:
    @staticmethod
    def sign_up(email, password):
        """
        Register a new user with Supabase
        """
        try:
            # Register with Supabase
            response = supabase_client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user and response.user.id:
                # Create a corresponding user in Django for session handling
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'is_active': True,
                    }
                )
                
                if created:
                    # Set unusable password as auth is handled by Supabase
                    user.set_unusable_password()
                    user.save()
                
                # Save Supabase user ID in the user model
                user.supabase_uid = response.user.id
                user.save()
                
                return user, True, None
            else:
                return None, False, "Registration failed"
        except Exception as e:
            logger.error(f"Supabase signup error: {str(e)}")
            return None, False, str(e)
    
    @staticmethod
    def sign_in(email, password):
        """
        Sign in a user with Supabase
        """
        try:
            # Sign in with Supabase
            response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.user.id:
                # Get or create the Django user for session handling
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'is_active': True,
                        'supabase_uid': response.user.id
                    }
                )
                
                if created:
                    user.set_unusable_password()
                    user.save()
                elif not hasattr(user, 'supabase_uid') or not user.supabase_uid:
                    user.supabase_uid = response.user.id
                    user.save()
                
                # Store the Supabase session token in the user session
                user.supabase_access_token = response.session.access_token
                user.supabase_refresh_token = response.session.refresh_token
                user.save()
                
                return user, True, None
            else:
                return None, False, "Authentication failed"
        except Exception as e:
            logger.error(f"Supabase signin error: {str(e)}")
            return None, False, str(e)
    
    @staticmethod
    def sign_out(user):
        """
        Sign out a user from Supabase
        """
        try:
            # Sign out from Supabase
            if hasattr(user, 'supabase_access_token') and user.supabase_access_token:
                supabase_client.auth.sign_out()
            
            # Clear Supabase tokens
            user.supabase_access_token = None
            user.supabase_refresh_token = None
            user.save()
            
            return True, None
        except Exception as e:
            logger.error(f"Supabase signout error: {str(e)}")
            return False, str(e) 