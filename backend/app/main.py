from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

app = FastAPI(title="AutoSRE API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = [
    {"id": "1", "name": "user-service", "type": "http", "port": 8081},
    {"id": "2", "name": "payment-service", "type": "http", "port": 8082},
    {"id": "3", "name": "inventory-service", "type": "http", "port": 8083},
]

INCIDENTS = []

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/services")
def get_services():
    data = []
    for svc in SERVICES:
        status = "healthy" if random.random() > 0.3 else "unhealthy"
        data.append({
            **svc,
            "status": status,
            "cpu": random.randint(20, 95),
            "memory": random.randint(30, 90),
            "latency": random.randint(50, 2000),
            "last_check": datetime.now().isoformat()
        })
    return data

@app.get("/api/v1/incidents")
def get_incidents(active: bool = True):
    if active:
        return [i for i in INCIDENTS if i["status"] != "resolved"]
    return INCIDENTS

@app.post("/api/v1/simulate/incident")
def simulate_incident():
    incident = {
        "id": str(len(INCIDENTS) + 1),
        "service_name": "payment-service",
        "type": "high_cpu",
        "severity": 0.8,
        "description": "High CPU usage detected",
        "status": "detected",
        "detected_at": datetime.now().isoformat()
    }
    INCIDENTS.append(incident)
    return {"success": True}

@app.post("/api/v1/services/{service_id}/restart")
def restart_service(service_id: str):
    return {
        "success": True,
        "message": f"Service {service_id} restarted"
    }

@app.get("/api/v1/ai/status")
def ai_status():
    return {
        "status": "active",
        "engine": "rule-based",
        "patterns_loaded": 5
    }
