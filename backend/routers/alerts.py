from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from core.database import get_db
from core.security import get_current_user
from models.alert import Alert
from schemas.alert import AlertResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    result = await db.execute(select(Alert).order_by(desc(Alert.created_at)).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
