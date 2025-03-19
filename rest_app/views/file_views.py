from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_app.config.cloudinary_config import upload_file, delete_file, get_files_in_folder
from rest_app.forms import FileUploadForm
from rest_app.models import CloudinaryFile
import os

@login_required
def upload_file_view(request):
    """View for uploading files to Cloudinary"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            folder = form.cleaned_data.get('folder', '')
            custom_filename = form.cleaned_data.get('custom_filename', '')
            
            # Get the original filename
            original_filename = os.path.splitext(file.name)[0]
            
            # Use custom filename if provided, otherwise use original
            filename = custom_filename if custom_filename else original_filename
            
            # Upload to Cloudinary
            result = upload_file(
                file, 
                folder=folder, 
                public_id=filename if custom_filename else None
            )
            
            if result['success']:
                # Save file info to database
                CloudinaryFile.objects.create(
                    user=request.user,
                    public_id=result['public_id'],
                    filename=filename,
                    url=result['url'],
                    resource_type=result['resource_type'],
                    format=result.get('format', ''),
                    folder=folder
                )
                messages.success(request, 'File uploaded successfully!')
                return redirect('user_home')
            else:
                messages.error(request, f"Upload failed: {result.get('error', 'Unknown error')}")
    else:
        form = FileUploadForm()
    
    return render(request, 'rest_app/upload_file.html', {'form': form})

@login_required
def delete_file_view(request, file_id):
    """View for deleting files from Cloudinary"""
    file = get_object_or_404(CloudinaryFile, id=file_id, user=request.user)
    
    if request.method == 'POST':
        # Delete from Cloudinary
        result = delete_file(file.public_id, resource_type=file.resource_type)
        
        if result['success']:
            # Delete from database
            file.delete()
            messages.success(request, 'File deleted successfully!')
        else:
            messages.error(request, f"Deletion failed: {result.get('error', 'Unknown error')}")
    
    return redirect('user_home')

@login_required
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