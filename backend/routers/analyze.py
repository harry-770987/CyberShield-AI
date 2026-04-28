import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user
from schemas.alert import NetworkAnalysisRequest, PhishingRequest, ThreatReport
from models.alert import Alert

from ml.network_ids import network_ids
from ml.log_anomaly import log_anomaly
from ml.phishing import phishing_detector
from ml.malware import malware_detector
from ml.fusion import fusion_engine

router = APIRouter()

async def save_alert(db: AsyncSession, report: ThreatReport, module: str, raw_input: dict):
    alert = Alert(
        id=report.session_id,
        module_name=module,
        threat_score=report.final_threat_score,
        severity=report.severity,
        severity_color=report.severity_color,
        module_scores=report.module_scores,
        recommendations=report.recommendations,
        raw_input=raw_input,
        detailed_results=report.detailed_results
    )
    db.add(alert)
    await db.commit()

@router.post("/network", response_model=ThreatReport)
async def analyze_network(request: NetworkAnalysisRequest, bg_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    result = network_ids.predict(request.features)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    fusion_result = fusion_engine.fuse({"network": result})
    report = ThreatReport(**fusion_result, detailed_results=result)
    bg_tasks.add_task(save_alert, db, report, "network", request.features)
    return report

@router.post("/log", response_model=ThreatReport)
async def analyze_log(log_file: UploadFile = File(...), bg_tasks: BackgroundTasks = BackgroundTasks(), db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    content = await log_file.read()
    text = content.decode('utf-8')
    result = log_anomaly.predict(text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    fusion_result = fusion_engine.fuse({"log": result})
    report = ThreatReport(**fusion_result, detailed_results=result)
    bg_tasks.add_task(save_alert, db, report, "log", {"filename": log_file.filename, "size": len(content)})
    return report

@router.post("/phishing", response_model=ThreatReport)
async def analyze_phishing(request: PhishingRequest, bg_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    result = phishing_detector.predict(request.url, request.email_body)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    fusion_result = fusion_engine.fuse({"phishing": result})
    report = ThreatReport(**fusion_result, detailed_results=result)
    bg_tasks.add_task(save_alert, db, report, "phishing", {"url": request.url, "email_body": request.email_body})
    return report

@router.post("/malware", response_model=ThreatReport)
async def analyze_malware(file: UploadFile = File(...), bg_tasks: BackgroundTasks = BackgroundTasks(), db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    content = await file.read()
    result = malware_detector.predict(content, file.filename)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    fusion_result = fusion_engine.fuse({"malware": result})
    report = ThreatReport(**fusion_result, detailed_results=result)
    bg_tasks.add_task(save_alert, db, report, "malware", {"filename": file.filename, "size": len(content)})
    return report

@router.post("/full", response_model=ThreatReport)
async def analyze_full(
    bg_tasks: BackgroundTasks,
    network_features: str = Form(None), 
    url: str = Form(None),
    email_body: str = Form(None),
    log_file: UploadFile = File(None),
    malware_file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    import json
    results = {}
    inputs = {}
    
    if network_features:
        try:
            feats = json.loads(network_features)
            results["network"] = network_ids.predict(feats)
            inputs["network"] = feats
        except Exception: pass
        
    if url:
        results["phishing"] = phishing_detector.predict(url, email_body)
        inputs["phishing"] = {"url": url, "email_body": email_body}
        
    if log_file:
        content = await log_file.read()
        results["log"] = log_anomaly.predict(content.decode('utf-8'))
        inputs["log"] = log_file.filename
        
    if malware_file:
        content = await malware_file.read()
        results["malware"] = malware_detector.predict(content, malware_file.filename)
        inputs["malware"] = malware_file.filename
        
    if not results:
         raise HTTPException(status_code=400, detail="No inputs provided for full scan")
         
    fusion_result = fusion_engine.fuse(results)
    report = ThreatReport(**fusion_result, detailed_results=results)
    bg_tasks.add_task(save_alert, db, report, "full", inputs)
    return report
