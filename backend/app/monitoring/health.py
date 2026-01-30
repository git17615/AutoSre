"""
Service health checking
"""
import aiohttp
import asyncio
from typing import Optional

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class HealthChecker:
    """HTTP health checker"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def check(self, service) -> bool:
        """Check if service is healthy"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Construct health URL
            # In production, use service discovery
            url = f"http://{service.name}:{service.port}{service.health_endpoint}"
            
            # Try container name first, then fallback to localhost for demo
            try:
                async with self.session.get(url, timeout=5) as response:
                    return response.status == 200
            except:
                # Fallback for demo
                url = f"http://localhost:{service.port}{service.health_endpoint}"
                async with self.session.get(url, timeout=5) as response:
                    return response.status == 200
                    
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False
        except Exception as e:
            logger.error(f"Health check error for {service.name}: {e}")
            return False