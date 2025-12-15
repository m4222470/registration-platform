from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app import schemas, crud
from app.api.dependencies import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.ApiResponse)
async def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    تسجيل مستخدم جديد - مطابق تماماً للواجهة الأمامية
    """
    try:
        # إنشاء المستخدم
        db_user = crud.UserCRUD.create_user(db, user_data)
        
        if not db_user:
            return {
                "success": False,
                "message": "البريد الإلكتروني مسجل مسبقاً",
                "status": "error",
                "data": None
            }
        
        # إنشاء رد الخادم (مطابق للواجهة الأمامية)
        response_data = {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone,
            "status": db_user.status,
            "message": "تم استلام طلبك بنجاح",
            "user_id": f"USER-{db_user.id:06d}",
            "review_time": "24-48 ساعة",
            "timestamp": datetime.now().isoformat(),
            "note": "سيتم مراجعة طلبك من قبل الإدارة"
        }
        
        return {
            "success": True,
            "message": "تم تسجيل بياناتك بنجاح",
            "status": "success",
            "data": response_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"حدث خطأ أثناء التسجيل: {str(e)}",
            "status": "error",
            "data": None
        }

@router.get("/users", response_model=schemas.ApiResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة المستخدمين
    """
    users = crud.UserCRUD.get_all_users(db, skip=skip, limit=limit)
    
    return {
        "success": True,
        "message": f"تم العثور على {len(users)} مستخدم",
        "data": users
    }

@router.get("/users/{user_id}", response_model=schemas.ApiResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    الحصول على مستخدم محدد
    """
    user = crud.UserCRUD.get_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    return {
        "success": True,
        "message": "تم العثور على المستخدم",
        "data": user
    }