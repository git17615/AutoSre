import random

class MetricsCollector:
    async def collect(self, service):
        return {
            "cpu_usage": random.randint(10, 95),
            "memory_usage": random.randint(20, 90),
            "latency_p95": random.randint(50, 2000),
            "error_rate": random.randint(0, 20)
        }
