from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.conf import settings
from rest_app.forms import CustomUserCreationForm, CustomAuthenticationForm, FileUploadForm
from rest_app.models import Account
from rest_app.services.auth_service import SupabaseAuthService
from rest_app.services.file_service import SupabaseFileService
from rest_app.utils.decorators import public_only

def home_view(request):
    """Home page view - the first page users will see"""
    return render(request, 'home.html')

@public_only
def login_view(request):
    """Login page view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user, success, error, tokens = SupabaseAuthService.sign_in(email, password)
            if success and user:
                # Store user information in session
                request.session["user_id"] = user.id
                request.session["user_email"] = user.email
                request.session["supabase_access_token"] = tokens.get('supabase_access_token')
                request.session["supabase_refresh_token"] = tokens.get('supabase_refresh_token')
                request.session.save()
                
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, error or 'Authentication failed')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@public_only
def register_view(request):
    """Registration page view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            
            user, success, error = SupabaseAuthService.sign_up(email, password)
            if success and user:
                messages.success(request, "Registration successful! Please verify your email.")
                return redirect(settings.LOGIN_URL)
            else:
                messages.error(request, error or 'Registration failed')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def user_home_view(request):
    """User home page - only accessible after login"""
    # This view should already be protected by the middleware
    
    # Get user files using the session user ID
    user_id = request.session.get("user_id")
    user_files = SupabaseFileService.get_user_files(user_id)
    
    return render(request, 'user_home.html', {
        'upload_form': FileUploadForm(),
        'user_files': user_files,
    })

def logout_view(request):
    """Logout the user and redirect to home page"""
    SupabaseAuthService.sign_out(request)
    return redirect(settings.LOGOUT_REDIRECT_URL) 