import aiohttp
import asyncio

class HealthChecker:
    async def check(self, service) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{service.name}:{service.port}{service.health_endpoint}"
                async with session.get(url, timeout=3) as r:
                    return r.status == 200
        except:
            return False
