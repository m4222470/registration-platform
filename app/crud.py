from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, date
import uuid

class UserCRUD:
    @staticmethod
    def create_user(db: Session, user_data: schemas.UserCreate):
        # التحقق من وجود البريد مسبقاً
        existing_user = db.query(models.User).filter(
            models.User.email == user_data.email
        ).first()
        
        if existing_user:
            return None
        
        # إنشاء مستخدم جديد
        db_user = models.User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            status="pending"  # الحالة الافتراضية
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # تحديث الإحصائيات
        stats = db.query(models.RegistrationStats).first()
        if stats:
            stats.total_users += 1
            stats.last_updated = datetime.now()
            db.commit()
        
        return db_user
    
    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user_status(db: Session, user_id: int, status: str):
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user.status = status
            user.updated_at = datetime.now()
            db.commit()
            db.refresh(user)
        return user

class StatsCRUD:
    @staticmethod
    def get_stats(db: Session):
        stats = db.query(models.RegistrationStats).first()
        
        if not stats:
            # إنشاء إحصائيات افتراضية إذا لم تكن موجودة
            stats = models.RegistrationStats(
                total_users=1247,
                today_visits=538,
                countries_count=18
            )
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        # زيادة زيارات اليوم (محاكاة)
        stats.today_visits += 1
        stats.last_updated = datetime.now()
        db.commit()
        
        return stats
    
    @staticmethod
    def update_stats(db: Session, total_users: int = None, 
                     today_visits: int = None, countries_count: int = None):
        stats = db.query(models.RegistrationStats).first()
        
        if not stats:
            stats = models.RegistrationStats()
            db.add(stats)
        
        if total_users is not None:
            stats.total_users = total_users
        if today_visits is not None:
            stats.today_visits = today_visits
        if countries_count is not None:
            stats.countries_count = countries_count
        
        stats.last_updated = datetime.now()
        db.commit()
        db.refresh(stats)
        
        return stats