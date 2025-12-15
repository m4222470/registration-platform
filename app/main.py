from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import sys

from app.core.config import settings
from app.database import engine, Base
from app.api.endpoints import users, stats

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء تطبيق FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend لمنصة التسجيل العربية - متوافق مع الواجهة الأمامية",
    docs_url="/docs",
    redoc_url="/redoc",
)

# إعداد CORS للتوافق مع Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """إنشاء الجداول عند بدء التطبيق"""
    logger.info("🚀 بدء تشغيل منصة التسجيل...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ تم إنشاء الجداول في قاعدة البيانات")

@app.on_event("shutdown")
async def shutdown_event():
    """التنظيف عند إيقاف التطبيق"""
    logger.info("🛑 إيقاف منصة التسجيل...")

# صفحة الترحيب
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "🟢 تعمل",
        "message": "مرحباً بك في منصة التسجيل - Backend",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "api_endpoints": {
            "register": "POST /api/register",
            "stats": "GET /api/stats",
            "users": "GET /api/users"
        }
    }

# صفحة حالة النظام
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }

# تسجيل نقاط API
app.include_router(users.router, prefix="/api", tags=["المستخدمين"])
app.include_router(stats.router, prefix="/api", tags=["الإحصائيات"])

# معالج الأخطاء العام
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"حدث خطأ: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "حدث خطأ داخلي في الخادم",
            "status": "error",
            "data": None
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
