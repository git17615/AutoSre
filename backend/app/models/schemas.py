from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class Service(BaseModel):
    id: str
    name: str
    type: str
    port: int
    health_endpoint: str = "/health"
    status: str = "unknown"
    last_check: Optional[datetime] = None
    metadata: Dict = {}

class Incident(BaseModel):
    id: str
    service_id: str
    service_name: str
    type: str
    severity: float
    description: str
    metrics: Dict

    status: str
    ai_analysis: Optional[Dict] = None
    action_taken: Optional[str] = None

    detected_at: datetime
    resolved_at: Optional[datetime] = None
