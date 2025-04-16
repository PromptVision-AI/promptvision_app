from rest_app.config.supabase_config import supabase_client
import logging
from rest_app.models import CloudinaryFile, Account

logger = logging.getLogger(__name__)

class SupabaseFileService:
    @staticmethod
    def create_file(user_id, file_data):
        """Create a file record in Supabase"""
        try:
            # Prepare the data for insert
            # data = {
            #     'user_id': user_id,
            #     'public_id': file_data['public_id'],
            #     'filename': file_data['filename'],
            #     'url': file_data['url'],
            #     'resource_type': file_data['resource_type'],
            #     'format': file_data.get('format', ''),
            #     'folder': file_data.get('folder', '')
            # }
            
            # Use the base model's insert method
            # result = CloudinaryFile.insert(data)
            result = CloudinaryFile.insert(file_data)
            return result
        except Exception as e:
            logger.error(f"File creation error: {str(e)}")
            return None

    @staticmethod
    def get_user_files(user_id):
        """Get all files for a user from Supabase"""
        try:
            if not user_id:
                return []
                
            # Use the base model's select_by_fields method
            fields = {'user_id': user_id}
            return CloudinaryFile.select_by_fields(fields=fields, order_by='created_at', desc=True)
        except Exception as e:
            logger.error(f"Get files error: {str(e)}")
            return []