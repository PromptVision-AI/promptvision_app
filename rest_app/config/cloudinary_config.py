import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Cloudinary
def initialize_cloudinary():
    """
    Initialize Cloudinary with credentials from environment variables.
    This function should be called once when the app starts.
    """
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )
    return cloudinary

# Initialize the client
cloudinary_client = initialize_cloudinary()
CLOUDINARY_FOLDER_NAME = os.getenv('CLOUDINARY_FOLDER_NAME', 'default_folder')

# File management functions
def upload_file(file, folder=None, public_id=None):
    """
    Upload a file to Cloudinary
    
    Args:
        file: The file to upload
        folder: Optional folder name to organize files
        public_id: Optional custom public ID for the file
        
    Returns:
        Dictionary with upload result information
    """
    upload_options = {
        'resource_type': 'auto',  # Automatically detect resource type
    }
    
    upload_options['folder'] = CLOUDINARY_FOLDER_NAME
    if folder:
        upload_options['folder'] += ("/" + folder)
    
    if public_id:
        upload_options['public_id'] = public_id
    
    try:
        result = cloudinary.uploader.upload(file, **upload_options)
        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'resource_type': result['resource_type'],
            'format': result.get('format', ''),
            'created_at': result['created_at']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def delete_file(public_id, resource_type='image'):
    """
    Delete a file from Cloudinary
    
    Args:
        public_id: The public ID of the file to delete
        resource_type: The resource type (image, video, raw)
        
    Returns:
        Dictionary with deletion result
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_files_in_folder(folder, resource_type='image', max_results=100):
    """
    Get a list of files in a specific folder
    
    Args:
        folder: The folder name to list files from
        resource_type: The resource type (image, video, raw)
        max_results: Maximum number of results to return
        
    Returns:
        List of files in the folder
    """
    try:
        result = cloudinary.api.resources(
            type='upload',
            prefix=folder,
            resource_type=resource_type,
            max_results=max_results
        )
        return {
            'success': True,
            'files': result['resources']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_file_info(public_id, resource_type='image'):
    """
    Get detailed information about a specific file
    
    Args:
        public_id: The public ID of the file
        resource_type: The resource type (image, video, raw)
        
    Returns:
        Dictionary with file information
    """
    try:
        result = cloudinary.api.resource(public_id, resource_type=resource_type)
        return {
            'success': True,
            'info': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def update_file(public_id, new_file=None, new_folder=None, new_public_id=None, resource_type='image'):
    """
    Update a file in Cloudinary
    
    Args:
        public_id: The public ID of the file to update
        new_file: Optional new file to replace the existing one
        new_folder: Optional new folder to move the file to
        new_public_id: Optional new public ID for the file
        resource_type: The resource type (image, video, raw)
        
    Returns:
        Dictionary with update result information
    """
    # If we're uploading a new file to replace the old one
    if new_file:
        # First delete the old file
        delete_result = delete_file(public_id, resource_type)
        if not delete_result['success']:
            return delete_result
        
        # Then upload the new file
        upload_options = {
            'resource_type': 'auto',
        }
        
        if new_folder:
            upload_options['folder'] = new_folder
        elif new_public_id:
            # If we have a new public ID but no new folder, extract folder from original public_id
            folder_parts = public_id.split('/')
            if len(folder_parts) > 1:
                upload_options['folder'] = '/'.join(folder_parts[:-1])
        
        # Use new_public_id if provided, otherwise use the filename part of the original public_id
        if new_public_id:
            upload_options['public_id'] = new_public_id
        else:
            upload_options['public_id'] = public_id.split('/')[-1]
        
        try:
            result = cloudinary.uploader.upload(new_file, **upload_options)
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'resource_type': result['resource_type'],
                'format': result.get('format', ''),
                'created_at': result['created_at']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # If we're just renaming or moving the file (no new file upload)
    elif new_folder or new_public_id:
        try:
            # Determine the new full public_id
            if new_folder and new_public_id:
                new_full_public_id = f"{new_folder}/{new_public_id}"
            elif new_folder:
                # Keep the original filename but change the folder
                original_filename = public_id.split('/')[-1]
                new_full_public_id = f"{new_folder}/{original_filename}"
            elif new_public_id:
                # Keep the original folder but change the filename
                folder_parts = public_id.split('/')
                if len(folder_parts) > 1:
                    original_folder = '/'.join(folder_parts[:-1])
                    new_full_public_id = f"{original_folder}/{new_public_id}"
                else:
                    new_full_public_id = new_public_id
            
            # Rename the file
            result = cloudinary.uploader.rename(
                public_id, 
                new_full_public_id,
                resource_type=resource_type
            )
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'resource_type': result['resource_type'],
                'format': result.get('format', ''),
                'created_at': result.get('created_at')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # If no changes were requested
    return {
        'success': False,
        'error': 'No update parameters provided'
    } 