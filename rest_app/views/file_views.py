from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_app.config.cloudinary_config import upload_file, delete_file, get_files_in_folder
from rest_app.forms import FileUploadForm
from rest_app.models import CloudinaryFile
from rest_app.services.file_service import SupabaseFileService
import os
from django.conf import settings
from datetime import datetime

def upload_file_view(request):
    """View for uploading files to Cloudinary and storing metadata in Supabase"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            folder = form.cleaned_data.get('folder', '')
            
            # Get the original custom filename
            original_custom_filename = form.cleaned_data.get('custom_filename', '')
            
            # Generate timestamp suffix in format YYYYMMDD_HHMMSS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Combine original filename with timestamp
            if original_custom_filename:
                custom_filename = f"{original_custom_filename}_{timestamp}"
            else:
                # If no custom filename was provided, use the original filename
                original_filename = os.path.splitext(file.name)[0]
                custom_filename = f"{original_filename}_{timestamp}"
            
            # Get user ID from session
            user_id = request.session.get("user_id")
            if not user_id:
                messages.error(request, "User authentication issue. Please log out and log in again.")
                return redirect(settings.LOGIN_REDIRECT_URL)
            
            # Upload to Cloudinary
            result = upload_file(
                file, 
                folder=folder, 
                public_id=custom_filename  # Always use the timestamped filename
            )
            
            if result['success']:
                # Save file info to Supabase
                file_data = {
                    'public_id': result['public_id'],
                    'filename': custom_filename,
                    'url': result['url'],
                    'resource_type': result['resource_type'],
                    'format': result.get('format', ''),
                    'folder': folder
                }
                
                # Create file record in Supabase
                created_file = SupabaseFileService.create_file(user_id, file_data)
                
                if created_file:
                    messages.success(request, "File uploaded successfully!")
                else:
                    messages.warning(request, "File uploaded to Cloudinary but record creation failed.")
            else:
                messages.error(request, "File upload failed.")
                
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = FileUploadForm()
    
    return render(request, 'upload_file.html', {'form': form})

def delete_file_view(request, file_id):
    """View for deleting files from Cloudinary and Supabase"""
    if request.method == 'POST':
        # Get user ID from session
        user_id = request.session.get("user_id")
        
        # Get the file details
        file = CloudinaryFile.select_by_id(file_id)
        
        # Check if the file exists and belongs to the user
        if file and file.get('user_id') == user_id:
            # Delete from Cloudinary
            delete_result = delete_file(file.get('public_id'), resource_type=file.get('resource_type'))
            
            if delete_result.get('success'):
                # Delete from Supabase
                delete_success = CloudinaryFile.delete_by_id(file_id)
                
                if delete_success:
                    messages.success(request, "File deleted successfully!")
                else:
                    messages.warning(request, "File deleted from Cloudinary but record deletion failed.")
            else:
                messages.error(request, "Failed to delete file from Cloudinary.")
        else:
            messages.error(request, "File not found or you don't have permission to delete it.")
            
    return redirect(settings.LOGIN_REDIRECT_URL)

def list_folder_files_view(request):
    """View for listing files in a specific folder"""
    folder = request.GET.get('folder', '')
    resource_type = request.GET.get('resource_type', 'image')
    
    if folder:
        result = get_files_in_folder(folder, resource_type=resource_type)
        files = result.get('files', []) if result['success'] else []
    else:
        files = []
    
    return render(request, 'list_folder_files.html', {
        'folder': folder,
        'files': files,
        'resource_type': resource_type
    }) 