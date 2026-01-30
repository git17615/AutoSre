"""
AutoSRE Agent Core with Local AI
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import docker

from app.agent.local_ai import local_ai
from app.monitoring.health import HealthChecker
from app.monitoring.metrics import MetricsCollector
from app.agent.actions import ActionExecutor
from app.models.schemas import Service, Incident, Action
from app.utils.logger import setup_logger
from app.api.websocket import manager as ws_manager

logger = setup_logger(__name__)

class AutoSREAgent:
    """Main AutoSRE agent with local AI"""
    
    def __init__(self):
        self.agent_id = f"autosre-{uuid.uuid4().hex[:8]}"
        self.services: Dict[str, Service] = {}
        self.incidents: Dict[str, Incident] = {}
        self.running = False
        
        # Initialize components
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        self.action_executor = ActionExecutor()
        
        # Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            self.docker_client = None
    
    async def initialize(self):
        """Initialize the agent"""
        logger.info(f"🔄 Initializing AutoSRE Agent: {self.agent_id}")
        await self.discover_services()
        logger.info(f"✅ Discovered {len(self.services)} services")
    
    async def discover_services(self):
        """Discover Docker containers with autosre labels"""
        if not self.docker_client:
            logger.warning("Docker not available, using demo services")
            await self.setup_demo_services()
            return
        
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                labels = container.labels
                
                if labels.get("autosre.monitor", "false").lower() == "true":
                    service = Service(
                        id=container.id[:12],
                        name=labels.get("autosre.service.name", container.name),
                        type=labels.get("autosre.service.type", "http"),
                        container_id=container.id,
                        image=container.image.tags[0] if container.image.tags else "unknown",
                        port=int(labels.get("autosre.service.port", "8080")),
                        health_endpoint=labels.get("autosre.health.endpoint", "/health"),
                        status="unknown",
                        created_at=datetime.now()
                    )
                    
                    self.services[service.id] = service
                    
                    # Notify WebSocket
                    await ws_manager.broadcast({
                        "type": "service_discovered",
                        "service": service.dict()
                    })
        
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            await self.setup_demo_services()
    
    async def setup_demo_services(self):
        """Setup demo services"""
        demo_services = [
            Service(
                id="user-svc",
                name="user-service",
                type="http",
                container_id="demo",
                image="user-service:demo",
                port=8081,
                health_endpoint="/health",
                status="healthy"
            ),
            Service(
                id="payment-svc",
                name="payment-service",
                type="http",
                container_id="demo",
                image="payment-service:demo",
                port=8082,
                health_endpoint="/health",
                status="healthy"
            ),
            Service(
                id="inventory-svc",
                name="inventory-service",
                type="http",
                container_id="demo",
                image="inventory-service:demo",
                port=8083,
                health_endpoint="/health",
                status="healthy"
            )
        ]
        
        for service in demo_services:
            self.services[service.id] = service
    
    async def start_monitoring_loop(self):
        """Main monitoring loop"""
        self.running = True
        logger.info("🔍 Starting monitoring loop")
        
        while self.running:
            try:
                # 1. Check service health
                await self.check_services_health()
                
                # 2. Collect metrics
                await self.collect_metrics()
                
                # 3. Analyze and act if needed
                if self.incidents:
                    await self.analyze_and_act()
                
                # Wait for next cycle
                await asyncio.sleep(30)  # Every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)
    
    async def check_services_health(self):
        """Check health of all services"""
        for service_id, service in self.services.items():
            try:
                is_healthy = await self.health_checker.check(service)
                
                if is_healthy:
                    service.status = "healthy"
                    service.last_check = datetime.now()
                    
                    # Resolve any active incidents for this service
                    self._resolve_service_incidents(service_id)
                    
                else:
                    service.status = "unhealthy"
                    service.last_check = datetime.now()
                    
                    # Create incident
                    incident = Incident(
                        id=str(uuid.uuid4()),
                        service_id=service_id,
                        service_name=service.name,
                        type="health",
                        severity=0.8,
                        description=f"Service {service.name} is unhealthy",
                        metrics={"health": "failed"},
                        status="detected",
                        detected_at=datetime.now()
                    )
                    
                    self.incidents[incident.id] = incident
                    
                    # Notify via WebSocket
                    await ws_manager.broadcast({
                        "type": "incident_detected",
                        "incident": incident.dict()
                    })
                    
            except Exception as e:
                logger.error(f"Health check failed for {service.name}: {e}")
    
    async def collect_metrics(self):
        """Collect metrics from services"""
        for service_id, service in self.services.items():
            try:
                metrics = await self.metrics_collector.collect(service)
                
                if metrics:
                    # Detect anomalies using local AI
                    anomaly = local_ai.detect_anomaly(metrics)
                    
                    if anomaly.get("is_anomaly", False):
                        # Create incident for anomaly
                        incident = Incident(
                            id=str(uuid.uuid4()),
                            service_id=service_id,
                            service_name=service.name,
                            type="anomaly",
                            severity=float(anomaly.get("probability", 0.5)),
                            description=f"Anomaly detected in {service.name}",
                            metrics=metrics,
                            status="detected",
                            detected_at=datetime.now()
                        )
                        
                        self.incidents[incident.id] = incident
                        
                        # Notify via WebSocket
                        await ws_manager.broadcast({
                            "type": "incident_detected",
                            "incident": incident.dict()
                        })
                        
            except Exception as e:
                logger.error(f"Metrics collection failed for {service.name}: {e}")
    
    async def analyze_and_act(self):
        """Analyze incidents and take action using local AI"""
        # Group incidents by service
        incidents_by_service = {}
        for incident_id, incident in self.incidents.items():
            if incident.status == "detected":
                if incident.service_id not in incidents_by_service:
                    incidents_by_service[incident.service_id] = []
                incidents_by_service[incident.service_id].append(incident)
        
        for service_id, service_incidents in incidents_by_service.items():
            service = self.services.get(service_id)
            if not service:
                continue
            
            # Analyze with local AI
            incidents_data = [inc.dict() for inc in service_incidents]
            analysis = local_ai.analyze_incident(incidents_data)
            
            # Decide action
            service_info = {
                "name": service.name,
                "type": service.type,
                "recent_restarts": service.metadata.get("restart_count", 0),
                "uptime_hours": 24  # demo
            }
            
            decision = local_ai.decide_action(analysis, service_info)
            
            # Take action if confidence is high enough
            if decision["action"] and decision["action"] != "monitor":
                await self.take_action(service, decision, service_incidents)
    
    async def take_action(self, service: Service, decision: Dict, incidents: List[Incident]):
        """Execute remediation action"""
        try:
            # Execute action
            result = await self.action_executor.execute(
                action=decision["action"],
                service=service
            )
            
            # Create action record
            action = Action(
                id=str(uuid.uuid4()),
                type=decision["action"],
                service_id=service.id,
                service_name=service.name,
                reason=decision.get("reason", ""),
                confidence=decision.get("confidence", 0.0),
                result=result,
                timestamp=datetime.now()
            )
            
            # Update incidents
            for incident in incidents:
                incident.status = "action_taken"
                incident.action_taken = decision["action"]
                incident.updated_at = datetime.now()
            
            # Notify via WebSocket
            await ws_manager.broadcast({
                "type": "action_taken",
                "action": action.dict()
            })
            
            # Verify after delay
            await asyncio.sleep(10)
            await self.verify_action(service, action)
            
        except Exception as e:
            logger.error(f"Action failed: {e}")
    
    async def verify_action(self, service: Service, action: Action):
        """Verify if action was successful"""
        try:
            is_healthy = await self.health_checker.check(service)
            
            if is_healthy:
                # Action successful
                service.status = "healthy"
                action.result["success"] = True
                
                # Resolve incidents
                for incident_id, incident in self.incidents.items():
                    if incident.service_id == service.id and incident.status == "action_taken":
                        incident.status = "resolved"
                        incident.resolved_at = datetime.now()
                
                # Notify via WebSocket
                await ws_manager.broadcast({
                    "type": "action_success",
                    "service_id": service.id,
                    "action_id": action.id
                })
                
            else:
                # Action failed
                action.result["success"] = False
                
                # Escalate or try different action
                await ws_manager.broadcast({
                    "type": "action_failed",
                    "service_id": service.id,
                    "action_id": action.id
                })
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
    
    def _resolve_service_incidents(self, service_id: str):
        """Resolve all incidents for a service"""
        for incident_id, incident in list(self.incidents.items()):
            if incident.service_id == service_id and incident.status == "detected":
                incident.status = "resolved"
                incident.resolved_at = datetime.now()
    
    async def shutdown(self):
        """Shutdown the agent"""
        self.running = False
        logger.info("🛑 Agent shutting down...")