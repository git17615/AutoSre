"""
API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.main import get_agent
from app.models.schemas import Service, Incident

router = APIRouter()

@router.get("/services", response_model=List[Service])
async def get_services():
    """Get all monitored services"""
    agent = get_agent()
    if agent:
        return list(agent.services.values())
    return []

@router.get("/services/{service_id}")
async def get_service(service_id: str):
    """Get specific service"""
    agent = get_agent()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not running")
    
    service = agent.services.get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return service

@router.get("/incidents", response_model=List[Incident])
async def get_incidents(active: bool = True):
    """Get incidents"""
    agent = get_agent()
    if not agent:
        return []
    
    if active:
        return [inc for inc in agent.incidents.values() if inc.status != "resolved"]
    return list(agent.incidents.values())

@router.post("/services/{service_id}/restart")
async def restart_service(service_id: str):
    """Manually restart a service"""
    agent = get_agent()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not running")
    
    service = agent.services.get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    try:
        # Execute restart action
        result = await agent.action_executor.execute("restart_service", service)
        
        return {
            "success": True,
            "message": f"Restarted {service.name}",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/status")
async def get_ai_status():
    """Get local AI status"""
    from app.agent.local_ai import local_ai
    
    return {
        "status": "active" if local_ai.model else "inactive",
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "anomaly_detection": "isolation-forest",
        "patterns_loaded": len(local_ai.incident_patterns)
    }

@router.post("/simulate/incident")
async def simulate_incident():
    """Simulate an incident for demo"""
    agent = get_agent()
    if not agent or not agent.services:
        raise HTTPException(status_code=404, detail="No services available")
    
    # Pick first service
    service = list(agent.services.values())[0]
    
    # Create simulated incident
    import uuid
    from datetime import datetime
    
    incident = Incident(
        id=str(uuid.uuid4()),
        service_id=service.id,
        service_name=service.name,
        type="simulated",
        severity=0.7,
        description=f"Simulated incident in {service.name}",
        metrics={"cpu": 95, "memory": 85, "latency": 2000},
        status="detected",
        detected_at=datetime.now()
    )
    
    agent.incidents[incident.id] = incident
    
    # Notify WebSocket
    from app.api.websocket import manager as ws_manager
    await ws_manager.broadcast({
        "type": "incident_detected",
        "incident": incident.dict()
    })
    
    return {
        "success": True,
        "message": f"Simulated incident created for {service.name}",
        "incident_id": incident.id
    }