from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RegistrationStats(Base):
    __tablename__ = "registration_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    total_users = Column(Integer, default=0)
    today_visits = Column(Integer, default=0)
    countries_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())