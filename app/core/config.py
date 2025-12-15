from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # إعدادات التطبيق
    APP_NAME: str = "منصة التسجيل - Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # قاعدة البيانات
    DATABASE_URL: str = "sqlite:///./registration.db"
    
    # إعدادات CORS للتوافق مع Netlify
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://your-netlify-site.netlify.app",  # ضع رابط Netlify هنا
        "*"  # للتطوير فقط
    ]
    
    # إعدادات الأمان
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()