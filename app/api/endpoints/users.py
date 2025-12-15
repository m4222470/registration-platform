# app/api/endpoints/users.py
"""
نقاط اتصال API لإدارة المستخدمين والتسجيل
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime
import uuid

from app import schemas, crud, models
from app.api.dependencies import get_db

router = APIRouter()

# ======================
# 1. نقطة التسجيل الرئيسية
# ======================
@router.post("/register", response_model=schemas.ApiResponse)
async def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    تسجيل مستخدم جديد - مطابق تماماً للواجهة الأمامية
    
    المعاملات:
    - name (مطلوب): الاسم الكامل (3-100 حرف)
    - email (مطلوب): البريد الإلكتروني
    - phone (اختياري): رقم الهاتف (05XXXXXXXX)
    - terms (مطلوب): الموافقة على الشروط
    
    الرد:
    - success: حالة العملية
    - message: رسالة توضيحية
    - data: بيانات المستخدم المسجل
    """
    try:
        # ========== التحقق من البيانات ==========
        print(f"📥 استلام طلب تسجيل: {user_data.dict()}")
        
        # التحقق من الموافقة على الشروط
        if not user_data.terms:
            return {
                "success": False,
                "message": "يجب الموافقة على الشروط والأحكام",
                "status": "error",
                "data": None
            }
        
        # ========== التحقق من وجود المستخدم ==========
        existing_user = db.query(models.User).filter(
            models.User.email == user_data.email
        ).first()
        
        if existing_user:
            return {
                "success": False,
                "message": "البريد الإلكتروني مسجل مسبقاً",
                "status": "error",
                "data": None
            }
        
        # ========== إنشاء المستخدم ==========
        print(f"🆕 إنشاء مستخدم جديد: {user_data.name}")
        
        db_user = models.User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            status="pending",  # الحالة الافتراضية
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ تم إنشاء المستخدم برقم: {db_user.id}")
        
        # ========== تحديث الإحصائيات ==========
        stats = db.query(models.RegistrationStats).first()
        if stats:
            stats.total_users += 1
            stats.last_updated = datetime.now()
            db.commit()
            print(f"📊 تم تحديث الإحصائيات: {stats.total_users} مستخدم")
        else:
            # إنشاء إحصائيات جديدة إذا لم تكن موجودة
            stats = models.RegistrationStats(
                total_users=1,
                today_visits=1,
                countries_count=1
            )
            db.add(stats)
            db.commit()
        
        # ========== إعداد الرد ==========
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
            "note": "سيتم مراجعة طلبك من قبل الإدارة",
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None
        }
        
        print(f"📤 إرسال رد للمستخدم: {db_user.email}")
        
        return {
            "success": True,
            "message": "تم تسجيل بياناتك بنجاح",
            "status": "success",
            "data": response_data
        }
        
    except IntegrityError as e:
        db.rollback()
        print(f"❌ خطأ في قاعدة البيانات: {str(e)}")
        return {
            "success": False,
            "message": "حدث خطأ في قاعدة البيانات",
            "status": "error",
            "data": None
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ غير متوقع: {str(e)}")
        return {
            "success": False,
            "message": f"حدث خطأ أثناء التسجيل: {str(e)}",
            "status": "error",
            "data": None
        }


# ======================
# 2. الحصول على جميع المستخدمين
# ======================
@router.get("/users", response_model=schemas.ApiResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع المستخدمين
    
    المعاملات:
    - skip (اختياري): عدد السجلات لتخطيها (للترقيم)
    - limit (اختياري): الحد الأقصى للسجلات (الافتراضي 100)
    
    الرد:
    - data: قائمة المستخدمين
    """
    try:
        users = crud.UserCRUD.get_all_users(db, skip=skip, limit=limit)
        
        # تحويل المستخدمين إلى قاموس
        users_list = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "status": user.status,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            users_list.append(user_dict)
        
        return {
            "success": True,
            "message": f"تم العثور على {len(users)} مستخدم",
            "data": {
                "users": users_list,
                "total": len(users_list),
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        print(f"❌ خطأ في جلب المستخدمين: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ في الخادم: {str(e)}"
        )


# ======================
# 3. الحصول على مستخدم محدد
# ======================
@router.get("/users/{user_id}", response_model=schemas.ApiResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    الحصول على بيانات مستخدم محدد
    
    المعاملات:
    - user_id (مطلوب): رقم المستخدم
    
    الرد:
    - data: بيانات المستخدم
    """
    try:
        user = crud.UserCRUD.get_user(db, user_id)
        
        if not user:
            return {
                "success": False,
                "message": f"المستخدم برقم {user_id} غير موجود",
                "status": "error",
                "data": None
            }
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "status": user.status,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        return {
            "success": True,
            "message": "تم العثور على المستخدم",
            "data": user_data
        }
        
    except Exception as e:
        print(f"❌ خطأ في جلب المستخدم: {str(e)}")
        return {
            "success": False,
            "message": f"حدث خطأ: {str(e)}",
            "status": "error",
            "data": None
        }


# ======================
# 4. تحديث حالة المستخدم
# ======================
@router.put("/users/{user_id}/status", response_model=schemas.ApiResponse)
async def update_user_status(
    user_id: int,
    status_data: dict,
    db: Session = Depends(get_db)
):
    """
    تحديث حالة المستخدم (للمسؤولين)
    
    المعاملات:
    - user_id (مطلوب): رقم المستخدم
    - status (مطلوب): الحالة الجديدة (pending, approved, rejected)
    
    الرد:
    - data: بيانات المستخدم المحدثة
    """
    try:
        status_value = status_data.get("status")
        
        if not status_value:
            return {
                "success": False,
                "message": "الحالة مطلوبة",
                "status": "error",
                "data": None
            }
        
        if status_value not in ["pending", "approved", "rejected"]:
            return {
                "success": False,
                "message": "الحالة غير صالحة. يجب أن تكون: pending, approved, rejected",
                "status": "error",
                "data": None
            }
        
        user = crud.UserCRUD.update_user_status(db, user_id, status_value)
        
        if not user:
            return {
                "success": False,
                "message": f"المستخدم برقم {user_id} غير موجود",
                "status": "error",
                "data": None
            }
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "status": user.status,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        return {
            "success": True,
            "message": f"تم تحديث حالة المستخدم إلى: {status_value}",
            "data": user_data
        }
        
    except Exception as e:
        print(f"❌ خطأ في تحديث حالة المستخدم: {str(e)}")
        return {
            "success": False,
            "message": f"حدث خطأ: {str(e)}",
            "status": "error",
            "data": None
        }


# ======================
# 5. البحث عن مستخدمين
# ======================
@router.get("/users/search/{query}", response_model=schemas.ApiResponse)
async def search_users(
    query: str,
    db: Session = Depends(get_db)
):
    """
    البحث عن مستخدمين بالاسم أو البريد الإلكتروني
    
    المعاملات:
    - query (مطلوب): نص البحث
    
    الرد:
    - data: نتائج البحث
    """
    try:
        # البحث في قاعدة البيانات
        users = db.query(models.User).filter(
            (models.User.name.ilike(f"%{query}%")) |
            (models.User.email.ilike(f"%{query}%"))
        ).all()
        
        users_list = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "status": user.status
            }
            users_list.append(user_dict)
        
        return {
            "success": True,
            "message": f"تم العثور على {len(users)} نتيجة للبحث: {query}",
            "data": {
                "results": users_list,
                "query": query,
                "count": len(users_list)
            }
        }
        
    except Exception as e:
        print(f"❌ خطأ في البحث: {str(e)}")
        return {
            "success": False,
            "message": f"حدث خطأ في البحث: {str(e)}",
            "status": "error",
            "data": None
        }


# ======================
# 6. جلب إحصائيات المستخدمين
# ======================
@router.get("/users/stats/summary", response_model=schemas.ApiResponse)
async def get_users_stats(
    db: Session = Depends(get_db)
):
    """
    الحصول على إحصائيات تفصيلية عن المستخدمين
    
    الرد:
    - data: إحصائيات المستخدمين
    """
    try:
        # إحصائيات حسب الحالة
        pending_count = db.query(models.User).filter(
            models.User.status == "pending"
        ).count()
        
        approved_count = db.query(models.User).filter(
            models.User.status == "approved"
        ).count()
        
        rejected_count = db.query(models.User).filter(
            models.User.status == "rejected"
        ).count()
        
        # المستخدمين النشطين
        active_count = db.query(models.User).filter(
            models.User.is_active == True
        ).count()
        
        # إجمالي المستخدمين
        total_count = db.query(models.User).count()
        
        # المستخدمين الجدد اليوم
        from datetime import date
        today = date.today()
        
        today_count = db.query(models.User).filter(
            models.User.created_at >= today
        ).count()
        
        stats_data = {
            "total_users": total_count,
            "active_users": active_count,
            "today_new_users": today_count,
            "by_status": {
                "pending": pending_count,
                "approved": approved_count,
                "rejected": rejected_count
            },
            "status_summary": f"{approved_count} موافق، {pending_count} بانتظار المراجعة، {rejected_count} مرفوض"
        }
        
        return {
            "success": True,
            "message": "إحصائيات المستخدمين",
            "data": stats_data
        }
        
    except Exception as e:
        print(f"❌ خطأ في جلب إحصائيات المستخدمين: {str(e)}")
        return {
            "success": False,
            "message": f"حدث خطأ: {str(e)}",
            "status": "error",
            "data": None
        }
