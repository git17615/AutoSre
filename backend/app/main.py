from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime
import uvicorn

app = FastAPI(title="AutoSRE API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
SERVICES = [
    {"id": "1", "name": "user-service", "type": "http", "port": 3001},
    {"id": "2", "name": "payment-service", "type": "http", "port": 3002},
    {"id": "3", "name": "inventory-service", "type": "http", "port": 3003}
]

@app.get("/")
def root():
    return {
        "message": "AutoSRE Platform",
        "version": "2.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/services")
def get_services():
    """Get all monitored services"""
    services_response = []
    for service in SERVICES:
        # Simulate random health status
        status = "healthy" if random.random() > 0.3 else "unhealthy"
        
        services_response.append({
            **service,
            "status": status,
            "cpu": random.randint(20, 95),
            "memory": random.randint(30, 90),
            "latency": random.randint(50, 500),
            "requests_per_minute": random.randint(100, 1000),
            "last_check": datetime.now().isoformat(),
            "health_endpoint": "/health"
        })
    
    return services_response

@app.get("/api/incidents")
def get_incidents():
    """Get current incidents"""
    incidents = []
    
    # Simulate some incidents
    if random.random() > 0.5:
        incidents.append({
            "id": "1",
            "service_name": "payment-service",
            "type": "high_cpu",
            "description": "High CPU usage detected (92%)",
            "severity": "high",
            "status": "active",
            "detected_at": datetime.now().isoformat(),
            "metrics": {"cpu": 92, "memory": 75, "latency": 450}
        })
    
    return incidents

@app.post("/api/services/{service_id}/restart")
def restart_service(service_id: str):
    """Manually restart a service"""
    return {
        "success": True,
        "message": f"Service {service_id} restarted successfully",
        "timestamp": datetime.now().isoformat(),
        "action": "restart"
    }

@app.get("/api/ai/status")
def get_ai_status():
    """Get AI engine status"""
    return {
        "status": "active",
        "engine": "local-ai",
        "model": "pattern-matching",
        "patterns_loaded": 5,
        "version": "1.0.0"
    }

@app.get("/api/metrics")
def get_metrics():
    """Get system metrics"""
    return {
        "total_services": len(SERVICES),
        "healthy_services": sum(1 for _ in SERVICES if random.random() > 0.3),
        "active_incidents": random.randint(0, 2),
        "ai_actions_taken": random.randint(0, 10),
        "uptime_hours": random.randint(1, 1000)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
