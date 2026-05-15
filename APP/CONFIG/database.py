from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent.parent/".env"
load_dotenv(dotenv_path=env_path)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")


def get_supabase(token: str = None) -> Client:
    client = create_client(url, key)
    if token:
        client.postgrest.auth(token)
    return client
