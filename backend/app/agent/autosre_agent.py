import uuid
from datetime import datetime

from app.core.health import HealthChecker
from app.core.metrics import MetricsCollector
from app.agent.local_ai import local_ai
from app.agent.action_executor import ActionExecutor
from app.models.schemas import Incident

class AutoSREAgent:
    def __init__(self):
        self.services = {}
        self.incidents = {}

        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        self.action_executor = ActionExecutor()

        self.auto_heal_enabled = True

    async def monitor_service(self, service):
        healthy = await self.health_checker.check(service)
        metrics = await self.metrics_collector.collect(service)

        if not healthy or metrics["cpu_usage"] > 90:
            await self.create_incident(service, metrics)

    async def create_incident(self, service, metrics):
        incident = Incident(
            id=str(uuid.uuid4()),
            service_id=service.id,
            service_name=service.name,
            type="auto_detected",
            severity=0.8,
            description="Anomaly detected",
            metrics=metrics,
            status="detected",
            detected_at=datetime.now()
        )

        self.incidents[incident.id] = incident
        await self.analyze_incident(incident)

    async def analyze_incident(self, incident):
        analysis = local_ai.analyze_incident([incident.dict()])
        incident.ai_analysis = analysis
        incident.status = "analyzed"

        if self.auto_heal_enabled:
            await self.take_action(incident)

    async def take_action(self, incident):
        decision = local_ai.decide_action(
            incident.ai_analysis,
            {"recent_restarts": 0, "uptime_hours": 5}
        )

        action = decision["action"]
        incident.action_taken = action
        incident.status = "action_taken"

        if action != "monitor":
            await self.action_executor.execute(action, incident.service_name)

        incident.status = "resolved"
        incident.resolved_at = datetime.now()
