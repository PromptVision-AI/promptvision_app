from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_HOST_URL')
supabase_key = os.getenv('SUPABASE_API_SECRET')
supabase_client = create_client(supabase_url, supabase_key) 

def get_new_supabase_client():
    return create_client(supabase_url, supabase_key)