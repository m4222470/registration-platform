from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

# نموذج التسجيل
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, regex="^05\d{8}$")
    terms: bool = Field(...)
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('الاسم يجب أن يكون 3 أحرف على الأقل')
        return v.strip()

# نموذج الرد
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    status: str
    message: str
    user_id: str
    review_time: str
    timestamp: datetime
    
    class Config:
        orm_mode = True  # تغيير from_attributes إلى orm_mode في Pydantic 1.x

# نموذج الإحصائيات
class StatsResponse(BaseModel):
    total_users: int
    today_visits: int
    countries_count: int
    last_updated: datetime

# نموذج الرد العام
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)
