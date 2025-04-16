from rest_app.config.supabase_config import supabase_client
import logging
import uuid

logger = logging.getLogger(__name__)

class SupabaseModelMixin:
    """
    Mixin that provides common Supabase database operations.
    All models that interact with Supabase should include this mixin.
    """
    # Subclasses should override this with their Supabase table name
    table_name = None

    @classmethod
    def select_by_id(cls, id_value):
        """
        Retrieve a record by its ID
        
        Args:
            id_value: The ID of the record to retrieve
            
        Returns:
            A dictionary with the record data or None if not found
        """
        if not cls.table_name:
            raise ValueError(f"table_name not defined for {cls.__name__}")
        
        try:
            result = supabase_client.table(cls.table_name)\
                .select('*')\
                .eq('id', id_value)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Supabase select_by_id error in {cls.table_name}: {str(e)}")
            return None

    @classmethod
    def select_by_fields(cls, fields=None, order_by=None, desc=False, limit=None):
        """
        Retrieve records matching the specified fields
        
        Args:
            fields: Dictionary of field names and values to filter by
            order_by: Field to order results by
            desc: Whether to order in descending order
            limit: Maximum number of records to return
            
        Returns:
            A list of dictionaries with the record data
        """
        if not cls.table_name:
            raise ValueError(f"table_name not defined for {cls.__name__}")
        
        try:
            query = supabase_client.table(cls.table_name).select('*')
            
            # Apply filters
            if fields:
                for field, value in fields.items():
                    query = query.eq(field, value)
            
            # Apply ordering
            if order_by:
                query = query.order(order_by, desc=desc)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase select_by_fields error in {cls.table_name}: {str(e)}")
            return []

    @classmethod
    def insert(cls, data):
        """
        Insert a new record
        
        Args:
            data: Dictionary of field names and values to insert
            
        Returns:
            The inserted record as a dictionary, or None if the operation failed
        """
        if not cls.table_name:
            raise ValueError(f"table_name not defined for {cls.__name__}")
        
        try:
            result = supabase_client.table(cls.table_name)\
                .insert(data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Supabase insert error in {cls.table_name}: {str(e)}")
            return None

    @classmethod
    def update_by_id(cls, id_value, data):
        """
        Update a record by its ID
        
        Args:
            id_value: The ID of the record to update
            data: Dictionary of field names and values to update
            
        Returns:
            The updated record as a dictionary, or None if the operation failed
        """
        if not cls.table_name:
            raise ValueError(f"table_name not defined for {cls.__name__}")
        
        try:            
            # Try a different approach with filter - ensuring UUID comparison
            result = supabase_client.table(cls.table_name) \
                .update(data) \
                .eq('id', id_value) \
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Supabase update_by_id error in {cls.table_name}: {str(e)}")
            return None

    @classmethod
    def delete_by_id(cls, id_value):
        """
        Delete a record by its ID
        
        Args:
            id_value: The ID of the record to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if not cls.table_name:
            raise ValueError(f"table_name not defined for {cls.__name__}")
        
        try:
            result = supabase_client.table(cls.table_name)\
                .delete()\
                .eq('id', id_value)\
                .execute()
            
            return True if result.data else False
        except Exception as e:
            logger.error(f"Supabase delete_by_id error in {cls.table_name}: {str(e)}")
            return False 
    
    @classmethod
    def select_by_field_in_list(cls, field_name, values, order_by=None, desc=False):
        """
        Retrieve records where a specific field is in a list of values.
        
        Args:
            field_name: Name of the field to apply the IN filter to
            values: List of values for the IN clause
            order_by: Optional field to order results
            desc: Descending order if True

        Returns:
            A list of matching records
        """
        if not cls.table_name:
            raise ValueError(f"table_name not defined for {cls.__name__}")
        
        try:
            query = supabase_client.table(cls.table_name).select('*')

            if values:
                query = query.in_(field_name, values)

            if order_by:
                query = query.order(order_by, desc=desc)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase select_by_field_in_list error in {cls.table_name}: {str(e)}")
            return []