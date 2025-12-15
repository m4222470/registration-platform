from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.api.dependencies import get_db

router = APIRouter()

@router.get("/stats", response_model=schemas.ApiResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    الحصول على الإحصائيات - مطابق للواجهة الأمامية
    """
    stats = crud.StatsCRUD.get_stats(db)
    
    response_data = {
        "total_users": stats.total_users,
        "today_visits": stats.today_visits,
        "countries_count": stats.countries_count,
        "last_updated": stats.last_updated.isoformat()
    }
    
    return {
        "success": True,
        "message": "تم جلب الإحصائيات بنجاح",
        "data": response_data
    }

@router.put("/stats/update", response_model=schemas.ApiResponse)
async def update_statistics(
    stats_data: schemas.StatsResponse,
    db: Session = Depends(get_db)
):
    """
    تحديث الإحصائيات (للمسؤولين)
    """
    updated_stats = crud.StatsCRUD.update_stats(
        db,
        total_users=stats_data.total_users,
        today_visits=stats_data.today_visits,
        countries_count=stats_data.countries_count
    )
    
    return {
        "success": True,
        "message": "تم تحديث الإحصائيات بنجاح",
        "data": updated_stats
    }