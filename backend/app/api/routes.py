from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from app.core.state import get_agent
from app.models.schemas import Service, Incident

router = APIRouter(prefix="/api/v1")


@router.get("/services", response_model=List[Service])
async def get_services():
    agent = get_agent()
    if not agent:
        return []
    return list(agent.services.values())


@router.get("/incidents", response_model=List[Incident])
async def get_incidents(active: bool = True):
    agent = get_agent()
    if not agent:
        return []

    if active:
        return [
            i for i in agent.incidents.values()
            if i.status != "resolved"
        ]

    return list(agent.incidents.values())


@router.post("/simulate/incident")
async def simulate_incident():
    agent = get_agent()
    if not agent or not agent.services:
        raise HTTPException(status_code=404, detail="No services found")

    svc = list(agent.services.values())[0]

    incident = Incident(
        id=str(uuid.uuid4()),
        service_id=svc.id,
        service_name=svc.name,
        type="simulated",
        severity=0.9,
        description="Simulated high CPU incident",
        metrics={"cpu": 95, "memory": 82},
        status="detected",
        detected_at=datetime.now()
    )

    agent.incidents[incident.id] = incident

    return {"success": True, "incident_id": incident.id}
