from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas.predict_schemas import (
    NetworkInput, NetworkResponse,
    AnomalyInput, AnomalyResponse,
    EmailInput, EmailResponse,
    UrlInput, UrlResponse
)
from ml import network_intrusion, anomaly_detection, email_phishing, url_detection
from core.config import settings

app = FastAPI(title="Cyber Threat Detection API", description="Multi-Layer ML API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Load all models on startup
    network_intrusion.load_model()
    anomaly_detection.load_model()
    email_phishing.load_model()
    url_detection.load_model()

@app.post("/predict/network", response_model=NetworkResponse)
def predict_network(data: NetworkInput):
    try:
        return network_intrusion.predict(data.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/anomaly", response_model=AnomalyResponse)
def predict_anomaly(data: AnomalyInput):
    try:
        return anomaly_detection.predict(data.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/email", response_model=EmailResponse)
def predict_email(data: EmailInput):
    try:
        return email_phishing.predict(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/url", response_model=UrlResponse)
def predict_url(data: UrlInput):
    try:
        return url_detection.predict(data.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "models_loaded": {
            "network": network_intrusion.is_loaded(),
            "anomaly": anomaly_detection.is_loaded(),
            "email": email_phishing.is_loaded(),
            "url": url_detection.is_loaded()
        }
    }
