# app/api/dependencies.py
"""
ملف التبعيات - يحتوي على دوال مساعدة تستخدم في نقاط الاتصال API
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    """
    دالة للحصول على جلسة قاعدة بيانات
    تُستخدم كنقطة تبعية في نقاط الاتصال API
    
    الاستخدام:
        @router.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === دالة تحقق من التوكن (للمستقبل) ===
# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db)
# ):
#     """
#     التحقق من صلاحية التوكن وإرجاع بيانات المستخدم
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     
#     try:
#         # فك تشفير التوكن
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     
#     # البحث عن المستخدم في قاعدة البيانات
#     user = db.query(models.User).filter(models.User.email == email).first()
#     if user is None:
#         raise credentials_exception
#     
#     return user


# === دوال تحقق إضافية (للمستقبل) ===
# def get_current_active_user(
#     current_user: models.User = Depends(get_current_user)
# ):
#     """
#     التحقق من أن المستخدم نشط
#     """
#     if not current_user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# def get_current_admin_user(
#     current_user: models.User = Depends(get_current_user)
# ):
#     """
#     التحقق من أن المستخدم له صلاحيات مدير
#     """
#     if not current_user.is_admin:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="ليس لديك صلاحية الوصول"
#         )
#     return current_user
