from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.connections = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    async def broadcast(self, message: dict):
        for ws in self.connections:
            await ws.send_json(message)

manager = WebSocketManager()
