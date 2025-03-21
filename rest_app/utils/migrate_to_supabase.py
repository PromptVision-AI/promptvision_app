#!/usr/bin/env python
import os
import sys
import importlib
import inspect
import django
from django.db import models
from django.apps import apps
from dotenv import load_dotenv
import logging
from supabase import create_client
import time

# Add the project root directory to the Python path
# This is needed to correctly import Django settings
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("supabase_migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_HOST_URL')
SUPABASE_KEY = os.getenv('SUPABASE_API_SECRET')

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promptvision_app.settings')
django.setup()

############ NOTE: UPDATE THIS LIST WITH ALL MODELS TO MIGRATE ############
from rest_app.models import Account, CloudinaryFile
MODELS_TO_MIGRATE = [Account, CloudinaryFile]
###########################################################################



def django_type_to_postgres(field, model=None):
    """Convert Django field type to PostgreSQL type"""
    if isinstance(field, models.AutoField) or isinstance(field, models.BigAutoField):
        return "bigserial"
    elif isinstance(field, models.CharField) or isinstance(field, models.TextField):
        max_length = getattr(field, 'max_length', None)
        if max_length:
            return f"varchar({max_length})"
        return "text"
    elif isinstance(field, models.IntegerField):
        return "integer"
    elif isinstance(field, models.BigIntegerField):
        return "bigint"
    elif isinstance(field, models.SmallIntegerField):
        return "smallint"
    elif isinstance(field, models.BooleanField):
        return "boolean"
    elif isinstance(field, models.DateField):
        return "date"
    elif isinstance(field, models.DateTimeField):
        return "timestamp with time zone"
    elif isinstance(field, models.TimeField):
        return "time"
    elif isinstance(field, models.DecimalField):
        return f"decimal({field.max_digits}, {field.decimal_places})"
    elif isinstance(field, models.FloatField):
        return "double precision"
    elif isinstance(field, models.JSONField):
        return "jsonb"
    elif isinstance(field, models.UUIDField):
        return "uuid"
    elif isinstance(field, models.ForeignKey):
        # If the related model has a primary key with a UUID type, use UUID type
        if field.related_model.__name__ == "Account":
            return "uuid"
        return "bigint"
    # Add more field types as needed
    return "text"  # Default to text for unknown types

def execute_sql(sql):
    """Execute raw SQL using Supabase REST API"""
    try:
        # Using the rpc function to execute raw SQL
        result = supabase.rpc(
            'exec_sql', 
            {'sql_query': sql}
        ).execute()
        return True, result
    except Exception as e:
        return False, str(e)

def check_rpc_function():
    """Check if the exec_sql RPC function exists in Supabase, create if not"""
    logger.info("Checking for SQL execution function in Supabase...")
    
    create_function_sql = """
    CREATE OR REPLACE FUNCTION exec_sql(sql_query TEXT)
    RETURNS JSONB
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    DECLARE
        result JSONB;
    BEGIN
        EXECUTE sql_query;
        result := '{"status": "success"}'::JSONB;
        RETURN result;
    EXCEPTION WHEN OTHERS THEN
        result := jsonb_build_object(
            'status', 'error',
            'message', SQLERRM,
            'detail', SQLSTATE
        );
        RETURN result;
    END;
    $$;
    """
    
    # We can't easily check if the function exists through the API
    # So we'll try to create/replace it
    try:
        # This requires superuser access in Supabase
        # You'll need to run this SQL in the Supabase dashboard/SQL editor first
        success, result = execute_sql(create_function_sql)
        if success:
            logger.info("SQL execution function created or updated successfully")
        else:
            logger.warning(f"Could not create SQL function: {result}")
            logger.warning("You may need to create this function manually in the Supabase dashboard SQL editor")
    except Exception as e:
        logger.warning(f"Error checking RPC function: {str(e)}")
        logger.warning("Please run the following SQL in the Supabase dashboard SQL editor:")
        logger.warning(create_function_sql)

def create_or_replace_table(model):
    """Create or replace a table in Supabase based on Django model"""
    # Use the table_name defined in the model if available
    if hasattr(model, 'table_name') and model.table_name:
        table_name = model.table_name
    # Otherwise, use the model name converted to lowercase
    else:
        table_name = model.__name__.lower()
    
    logger.info(f"Processing model: {model.__name__} (table: {table_name})")
    
    # Generate column definitions for Supabase
    columns = []
    foreign_keys = []
    
    # First, check if this is the Account model
    is_account_model = model.__name__ == 'Account'
    
    # Add UUID primary key for Account model
    if is_account_model:
        columns.append({
            "name": "id",
            "type": "uuid",
            "primary": True,
            "nullable": False,
            "default": "auth.uid()"
        })
    
    # Process each field
    for field in model._meta.fields:
        # Skip if its the ID field for the Account model, we already handled it
        if is_account_model and field.name == 'id':
            continue

        field_type = django_type_to_postgres(field, model)
        field_dict = {
            "name": field.name if not isinstance(field, models.ForeignKey) else f"{field.name}_id",
            "type": field_type,
            "nullable": field.null,
        }
        
        # Add default for BooleanField
        if isinstance(field, models.BooleanField) and field.default is not models.NOT_PROVIDED:
            field_dict["default"] = "true" if field.default else "false"
            
        # Handle auto fields
        if isinstance(field, models.AutoField) or isinstance(field, models.BigAutoField):
            field_dict["primary"] = True
            
        # Handle foreign keys
        if isinstance(field, models.ForeignKey):
            related_model = field.related_model
            related_table = related_model.table_name if hasattr(related_model, 'table_name') and related_model.table_name else related_model.__name__.lower()
            
            # If the related model is Account, ensure we use UUID type
            field_type = "uuid" if related_model.__name__ == "Account" else field_type
            field_dict["type"] = field_type
            
            foreign_keys.append({
                "column": f"{field.name}_id",
                "references": related_table,
                "ref_column": "id"
            })
            
        columns.append(field_dict)
    
    # Generate SQL for dropping the table if it exists
    sql_drop = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
    
    # Generate SQL for creating the table
    sql_create = f"CREATE TABLE {table_name} (\n"
    
    # Add column definitions
    for i, col in enumerate(columns):
        sql_create += f"  {col['name']} {col['type']}"
        
        if col.get("primary", False):
            sql_create += " PRIMARY KEY"
            
        if not col.get("nullable", True):
            sql_create += " NOT NULL"
            
        if "default" in col:
            sql_create += f" DEFAULT {col['default']}"
            
        if i < len(columns) - 1 or foreign_keys:
            sql_create += ","
            
        sql_create += "\n"
    
    # Add foreign key constraints
    for i, fk in enumerate(foreign_keys):
        sql_create += f"  CONSTRAINT {table_name}_{fk['column']}_fkey FOREIGN KEY ({fk['column']}) REFERENCES {fk['references']}({fk['ref_column']}) ON DELETE CASCADE"
        
        if i < len(foreign_keys) - 1:
            sql_create += ","
            
        sql_create += "\n"
    
    sql_create += ");"
    
    # Execute the SQL to create the table
    try:
        # First drop the table if it exists
        execute_sql(sql_drop)
        
        # Then create the table
        result = execute_sql(sql_create)
        logger.info(f"Table {table_name} created successfully")
        
        # Add timestamp trigger for updated_at field
        if any(col['name'] == 'updated_at' for col in columns):
            sql_trigger = f"""
            CREATE OR REPLACE FUNCTION update_{table_name}_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = current_timestamp;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS set_{table_name}_timestamp ON {table_name};
            
            CREATE TRIGGER set_{table_name}_timestamp
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION update_{table_name}_timestamp();
            """
            execute_sql(sql_trigger)
            logger.info(f"Created update timestamp trigger for {table_name}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to create table {table_name}: {str(e)}")
        return False

def migrate_all_models():
    """Migrate all Django models to Supabase"""
    logger.info("Starting migration of Django models to Supabase")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Supabase credentials not found in environment variables")
        return False

    # Check/create the SQL execution function
    check_rpc_function()
    
    # Use the predefined models list
    all_models = MODELS_TO_MIGRATE
    logger.info(f"Using {len(all_models)} predefined models")
    
    if len(all_models) == 0:
        logger.warning("No models found. Check your model paths and imports.")
        return False
    
    # Sort models by dependencies (CustomUser first, then models that depend on it)
    sorted_models = []
    dependency_models = set()
    
    # First pass: find models with dependencies
    for model in all_models:
        for field in model._meta.fields:
            if isinstance(field, models.ForeignKey):
                dependency_models.add(field.related_model)
    
    # Second pass: add dependencies first, then the rest
    for model in all_models:
        if model in dependency_models:
            sorted_models.append(model)
    
    # Add the remaining models
    for model in all_models:
        if model not in sorted_models:
            sorted_models.append(model)
    
    # Create tables for each model in order
    for model in sorted_models:
        create_or_replace_table(model)
    
    logger.info("Migration complete!")
    return True

if __name__ == "__main__":
    migrate_all_models() 