class LocalAI:
    def analyze_incident(self, incidents):
        return {
            "root_cause": "High CPU usage",
            "confidence": 0.82,
            "recommended_action": "restart_service"
        }

    def decide_action(self, analysis, service_info):
        if analysis["confidence"] >= 0.7:
            return {
                "action": analysis["recommended_action"],
                "confidence": analysis["confidence"]
            }

        return {"action": "monitor", "confidence": analysis["confidence"]}

local_ai = LocalAI()
