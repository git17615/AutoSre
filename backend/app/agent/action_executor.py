class ActionExecutor:
    async def execute(self, action: str, service):
        if action == "restart_service":
            return {"action": "restart", "success": True}

        if action == "scale_up":
            return {"action": "scale_up", "success": True}

        return {"action": "none", "success": False}
