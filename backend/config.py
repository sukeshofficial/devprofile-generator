import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
    
    # JWT Settings
    SECRET_KEY = os.getenv("sukesh-is-a-creator")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Database Settings
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # Redis Settings
    REDIS_URL = os.getenv("REDIS_URL", "")
    
    # GitHub OAuth Settings
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
    
    # App Settings
    APP_NAME = "DevProfile Generator"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()
