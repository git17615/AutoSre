from app.models.schemas import Service

_agent = None


class AutoSREAgent:
    def __init__(self):
        self.services = {}
        self.incidents = {}


def get_agent():
    global _agent
    if _agent is None:
        _agent = AutoSREAgent()
        _seed_services(_agent)
    return _agent


def _seed_services(agent):
    services = [
        Service(
            id="svc-1",
            name="payment-service",
            type="http",
            port=8080
        ),
        Service(
            id="svc-2",
            name="user-service",
            type="http",
            port=8081
        )
    ]

    for svc in services:
        agent.services[svc.id] = svc
