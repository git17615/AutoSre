import asyncio

class Scheduler:
    def __init__(self, agent):
        self.agent = agent
        self.running = True

    async def start(self):
        while self.running:
            for service in self.agent.services.values():
                await self.agent.monitor_service(service)
            await asyncio.sleep(5)
