from django.conf import settings
from rest_app.models import Account
from rest_app.config.supabase_config import supabase_client, get_new_supabase_client
import logging
import jwt as pyjwt
import time
import os
from dotenv import load_dotenv
from supabase import create_client

logger = logging.getLogger(__name__)

load_dotenv()
JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

class SupabaseAuthService:
    @staticmethod
    def sign_up(email, password):
        """Register a new user with Supabase"""
        try:
            # Register with Supabase
            response = supabase_client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user and response.user.id:
                # Create Django user first
                try:
                    # Insert data into Supabase
                    user_data = {
                        'id': response.user.id,
                        'email': email,
                        # 'supabase_access_token': response.session.access_token,
                        # 'supabase_refresh_token': response.session.refresh_token
                    }
                    
                    # Try to insert, catch and handle any errors
                    try:
                        Account.insert(user_data)
                    except Exception as e:
                        logger.error(f"Supabase user insert error: {str(e)}")
                        # This shouldn't prevent login if only the Supabase insert fails
                    
                    return response.user, True, None
                    
                except Exception as e:
                    logger.error(f"Django user creation error: {str(e)}")
                    return None, False, f"User creation failed: {str(e)}"
            else:
                return None, False, "Registration failed"
        except Exception as e:
            logger.error(f"Supabase signup error: {str(e)}")
            return None, False, str(e)
    
    @staticmethod
    def sign_in(email, password):
        """Sign in a user with Supabase"""
        try:
            # Sign in with Supabase
            response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.user.id:
                # Get or create Django user

                try:
                    user = response.user
                    # Update tokens in Supabase
                    try:
                        Account.update_by_id(
                            response.user.id,
                            {
                                'supabase_access_token': response.session.access_token,
                                'supabase_refresh_token': response.session.refresh_token,
                            }
                        )
                    except Exception as e:
                        logger.error(f"Supabase token update error: {str(e)}")
                        # Continue even if update fails
                    
                    return user, True, None, {'supabase_access_token': response.session.access_token, 
                                              'supabase_refresh_token': response.session.refresh_token,}
                    
                except Exception as e:
                    logger.error(f"Django user retrieval/creation error: {str(e)}")
                    return None, False, f"User retrieval failed: {str(e)}", {}
            else:
                return None, False, "Authentication failed"
        except Exception as e:
            logger.error(f"Supabase signin error: {str(e)}")
            return None, False, str(e), {}
    
    @staticmethod
    def sign_out(request):
        """Sign out a user from Supabase"""
        try:
            # Also update in Supabase if possible
            try:
                Account.update_by_id(
                    request.session.get("user_id"),
                    {
                        'supabase_access_token': None,
                        'supabase_refresh_token': None,
                    }
                )
            except Exception:
                # Ignore errors when updating Supabase during logout
                pass

            for key in ['supabase_access_token', 'supabase_refresh_token', 'user_id', 'user_email']:
                if key in request.session:
                    del request.session[key]
                
            # Save the session
            request.session.save()
            
            return True, None
        except Exception as e:
            logger.error(f"Supabase signout error: {str(e)}")
            return False, str(e) 
    
    @staticmethod
    def _validate_token(request):
        """Validate the Supabase access token"""
        try:
            # Check if token exists in session
            token = request.session.get("supabase_access_token")
            
            if not token:
                logger.error("No access token found in session")
                return False
                
            # Decode token without verification to check expiration
            try:
                # Use PyJWT correctly
                decoded = pyjwt.decode(token, JWT_SECRET, options={"verify_signature": False})
                exp = decoded.get('exp', 0)
                
                # If token is valid for more than 5 minutes
                if exp - time.time() > 300:
                    return True
                    
                # If token is expired or about to expire, try to refresh
                logger.info("Token is about to expire, refreshing...")
            except Exception as decode_error:
                logger.error(f"Failed to decode token: {str(decode_error)}")
                return False
                
            try:
                # Set auth token for the current session
                personal_supabase_client = get_new_supabase_client()
                personal_supabase_client.auth.set_session(
                    request.session.get("supabase_access_token"),
                    request.session.get("supabase_refresh_token")
                )
                
                # Refresh the token
                response = personal_supabase_client.auth.refresh_session()
                
                if response and response.session:
                    print("REFRESH TOKEN SUCCESS")
                    print(response.session)
                    # Update the user's tokens
                    request.session["supabase_access_token"] = response.session.access_token
                    request.session["supabase_refresh_token"] = response.session.refresh_token
                    request.session.save()
                    
                    # Also update in Supabase
                    Account.update_by_id(
                        request.session["user_id"],
                        {
                            'supabase_access_token': response.session.access_token,
                            'supabase_refresh_token': response.session.refresh_token,
                        }
                    )
                    
                    return True
                    
                return False
            except Exception as e:
                logger.error(f"Token refresh error: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return False