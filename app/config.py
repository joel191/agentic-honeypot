import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "dev-secret-key")
