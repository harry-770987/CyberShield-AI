from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from core.security import get_current_user
from models.alert import Alert
from schemas.alert import DashboardStats
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    today = datetime.utcnow().date()
    
    result_total = await db.execute(select(func.count(Alert.id)))
    total_alerts = result_total.scalar()
    
    result_critical_today = await db.execute(select(func.count(Alert.id)).where(Alert.severity == "CRITICAL", func.date(Alert.created_at) == today))
    critical_today = result_critical_today.scalar()
    
    result_avg = await db.execute(select(func.avg(Alert.threat_score)).where(func.date(Alert.created_at) == today))
    avg_threat_score = result_avg.scalar() or 0.0
    
    result_top = await db.execute(select(func.max(Alert.threat_score)).where(func.date(Alert.created_at) == today))
    top_threat = result_top.scalar() or 0.0
    
    # Severity breakdown
    by_severity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    severity_query = await db.execute(select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity))
    for row in severity_query.all():
        if row[0] in by_severity:
            by_severity[row[0]] = row[1]
            
    # Module breakdown
    by_module = {"network": 0, "log": 0, "phishing": 0, "malware": 0, "full":0}
    module_query = await db.execute(select(Alert.module_name, func.count(Alert.id)).group_by(Alert.module_name))
    for row in module_query.all():
        if row[0] in by_module:
            by_module[row[0]] = row[1]
            
    # Last 7 days
    alerts_7_days = []
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        
        counts = {"LOW":0, "MEDIUM":0, "HIGH":0, "CRITICAL":0}
        q = await db.execute(select(Alert.severity, func.count(Alert.id)).where(func.date(Alert.created_at) == target_date).group_by(Alert.severity))
        for row in q.all():
            if row[0] in counts:
                counts[row[0]] = row[1]
                
        alerts_7_days.append({
            "date": target_date.strftime("%Y-%m-%d"),
            "low": counts["LOW"],
            "medium": counts["MEDIUM"],
            "high": counts["HIGH"],
            "critical": counts["CRITICAL"]
        })
        
    return DashboardStats(
        total_alerts=total_alerts,
        critical_today=critical_today,
        avg_threat_score_today=float(avg_threat_score),
        by_severity=by_severity,
        by_module=by_module,
        alerts_last_7_days=alerts_7_days,
        top_threat_today=float(top_threat)
    )
