from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from rest_app.forms import CustomUserCreationForm, CustomAuthenticationForm, FileUploadForm
from rest_app.models import CloudinaryFile

def home_view(request):
    """Home page view - the first page users will see"""
    return render(request, 'home.html')


def login_view(request):
    """Login page view"""
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def register_view(request):
    """Registration page view"""
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


@login_required
def user_home_view(request):
    """User home page - only accessible after login"""
    # Get user's files
    user_files = CloudinaryFile.objects.filter(user=request.user).order_by('-created_at')
    
    # Get form for file upload
    upload_form = FileUploadForm()
    
    return render(request, 'user_home.html', {
        'user_files': user_files,
        'upload_form': upload_form
    })


def logout_view(request):
    """Logout the user and redirect to home page"""
    logout(request)
    return redirect('home') 