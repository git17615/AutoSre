from fastapi import APIRouter, HTTPException
from typing import List

from app.main import get_agent
from app.models.schemas import Service, Incident

router = APIRouter()

@router.get("/services", response_model=List[Service])
async def services():
    agent = get_agent()
    return list(agent.services.values()) if agent else []

@router.get("/incidents", response_model=List[Incident])
async def incidents(active: bool = True):
    agent = get_agent()
    if not agent:
        return []
    return [
        i for i in agent.incidents.values()
        if not active or i.status != "resolved"
    ]

@router.post("/services/{service_id}/restart")
async def restart(service_id: str):
    agent = get_agent()
    if not agent or service_id not in agent.services:
        raise HTTPException(404, "Service not found")

    result = await agent.action_executor.execute(
        "restart_service",
        agent.services[service_id]
    )
    return {"success": True, "result": result}

@router.get("/ai/status")
async def ai_status():
    from app.agent.local_ai import local_ai
    return {
        "status": "active" if local_ai.model else "inactive",
        "patterns_loaded": len(local_ai.incident_patterns)
    }

@router.post("/simulate/incident")
async def simulate_incident():
    agent = get_agent()
    if not agent or not agent.services:
        raise HTTPException(404, "No services")

    import uuid
    from datetime import datetime
    from app.models.schemas import Incident

    svc = list(agent.services.values())[0]
    inc = Incident(
        id=str(uuid.uuid4()),
        service_id=svc.id,
        service_name=svc.name,
        type="simulated",
        severity=0.8,
        description="Simulated failure",
        metrics={"cpu": 95, "memory": 80},
        status="detected",
        detected_at=datetime.now()
    )

    agent.incidents[inc.id] = inc
    return {"success": True, "incident_id": inc.id}
