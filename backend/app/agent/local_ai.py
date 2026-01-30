"""
Local AI model for reasoning without external API calls
"""
import json
import numpy as np
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class LocalAI:
    """Local AI model using sentence transformers and ML"""
    
    def __init__(self):
        self.model = None
        self.anomaly_detector = None
        self.scaler = None
        self.model_path = "/app/data/local_ai_models"
        
        # Incident patterns database
        self.incident_patterns = {
            "high_cpu_low_memory": {
                "symptoms": ["cpu high", "memory normal", "latency increased"],
                "root_cause": "CPU-bound process or infinite loop",
                "action": "restart_service",
                "confidence": 0.8
            },
            "high_memory": {
                "symptoms": ["memory high", "cpu normal", "latency normal"],
                "root_cause": "Memory leak or cache bloat",
                "action": "restart_service",
                "confidence": 0.7
            },
            "high_latency": {
                "symptoms": ["latency high", "cpu normal", "memory normal"],
                "root_cause": "Database slow or external API timeout",
                "action": "scale_up",
                "confidence": 0.6
            },
            "service_down": {
                "symptoms": ["health failed", "cpu zero", "memory zero"],
                "root_cause": "Process crashed or OOM killed",
                "action": "restart_service",
                "confidence": 0.9
            },
            "network_issue": {
                "symptoms": ["latency spiked", "errors increased", "cpu normal"],
                "root_cause": "Network congestion or DNS issues",
                "action": "retry_and_throttle",
                "confidence": 0.5
            }
        }
        
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize local ML models"""
        try:
            # Load sentence transformer model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Local AI model loaded")
            
            # Initialize anomaly detector
            self.anomaly_detector = IsolationForest(
                n_estimators=100,
                contamination=0.1,
                random_state=42
            )
            self.scaler = StandardScaler()
            
            # Load or train with initial data
            self._train_initial_model()
            
        except Exception as e:
            logger.error(f"Failed to initialize local AI: {e}")
            self.model = None
    
    def _train_initial_model(self):
        """Train initial anomaly detection model with synthetic data"""
        # Generate synthetic normal metrics
        normal_data = []
        for _ in range(1000):
            # Normal ranges
            cpu = np.random.normal(30, 10)  # ~30% avg
            memory = np.random.normal(50, 15)  # ~50% avg
            latency = np.random.normal(100, 30)  # ~100ms avg
            errors = np.random.poisson(5)  # ~5 errors/min
            normal_data.append([cpu, memory, latency, errors])
        
        normal_data = np.array(normal_data)
        normal_data = np.clip(normal_data, 0, 100)
        
        # Fit scaler and anomaly detector
        self.scaler.fit(normal_data)
        scaled_data = self.scaler.transform(normal_data)
        self.anomaly_detector.fit(scaled_data)
        
        # Save models
        os.makedirs(self.model_path, exist_ok=True)
        joblib.dump(self.anomaly_detector, f"{self.model_path}/anomaly_detector.joblib")
        joblib.dump(self.scaler, f"{self.model_path}/scaler.joblib")
    
    def detect_anomaly(self, metrics: Dict[str, float]) -> Dict:
        """Detect anomalies using local ML model"""
        try:
            # Prepare features
            features = np.array([[
                metrics.get('cpu_usage', 0),
                metrics.get('memory_usage', 0),
                metrics.get('latency_p95', 0),
                metrics.get('error_rate', 0)
            ]])
            
            # Scale and predict
            features_scaled = self.scaler.transform(features)
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
            
            # Convert to probability (0-1, higher = more anomalous)
            anomaly_prob = 1 / (1 + np.exp(-anomaly_score))
            
            return {
                "is_anomaly": bool(is_anomaly),
                "score": float(anomaly_score),
                "probability": float(anomaly_prob),
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {
                "is_anomaly": False,
                "score": 0.0,
                "probability": 0.0,
                "metrics": metrics,
                "error": str(e)
            }
    
    def analyze_incident(self, incidents: List[Dict]) -> Dict:
        """Analyze incidents using pattern matching and embeddings"""
        if not incidents:
            return {"root_cause": "No incidents", "confidence": 0.0, "action": None}
        
        # Combine incident descriptions
        combined_text = " ".join([
            f"{inc.get('type', '')} {inc.get('description', '')} "
            f"severity:{inc.get('severity', 0)}"
            for inc in incidents
        ])
        
        # Get embedding
        if self.model:
            embedding = self.model.encode(combined_text)
            
            # Find similar patterns (simplified cosine similarity)
            best_match = None
            best_score = -1
            
            for pattern_name, pattern in self.incident_patterns.items():
                pattern_text = " ".join(pattern["symptoms"])
                pattern_embedding = self.model.encode(pattern_text)
                
                # Cosine similarity
                similarity = np.dot(embedding, pattern_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(pattern_embedding)
                )
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = pattern_name
            
            if best_match and best_score > 0.3:  # Threshold
                pattern = self.incident_patterns[best_match]
                return {
                    "root_cause": pattern["root_cause"],
                    "confidence": pattern["confidence"] * best_score,
                    "action": pattern["action"],
                    "pattern_matched": best_match,
                    "similarity_score": float(best_score)
                }
        
        # Fallback: Rule-based analysis
        return self._rule_based_analysis(incidents)
    
    def _rule_based_analysis(self, incidents: List[Dict]) -> Dict:
        """Rule-based incident analysis"""
        incident_types = [inc.get('type', '') for inc in incidents]
        severities = [inc.get('severity', 0) for inc in incidents]
        
        if any('health' in t for t in incident_types):
            return {
                "root_cause": "Service health check failed",
                "confidence": 0.85,
                "action": "restart_service",
                "reason": "health_check_failed"
            }
        elif any('cpu' in t for t in incident_types):
            max_cpu = max([inc.get('metrics', {}).get('cpu_usage', 0) for inc in incidents])
            return {
                "root_cause": f"High CPU usage ({max_cpu:.1f}%)",
                "confidence": 0.75,
                "action": "restart_service" if max_cpu > 90 else "scale_up",
                "reason": "cpu_bound"
            }
        elif any('memory' in t for t in incident_types):
            return {
                "root_cause": "Memory pressure or leak",
                "confidence": 0.7,
                "action": "restart_service",
                "reason": "memory_issue"
            }
        elif any('latency' in t for t in incident_types):
            return {
                "root_cause": "Performance degradation",
                "confidence": 0.6,
                "action": "scale_up",
                "reason": "high_latency"
            }
        else:
            return {
                "root_cause": "Unknown issue - needs investigation",
                "confidence": 0.3,
                "action": "investigate",
                "reason": "unknown"
            }
    
    def decide_action(self, analysis: Dict, service_info: Dict) -> Dict:
        """Decide on remediation action with safety checks"""
        action = analysis.get("action")
        confidence = analysis.get("confidence", 0.0)
        
        # Safety rules
        recent_restarts = service_info.get("recent_restarts", 0)
        service_uptime = service_info.get("uptime_hours", 0)
        
        # Don't restart if already restarted recently
        if action == "restart_service" and recent_restarts >= 2:
            return {
                "action": "scale_up",
                "reason": "Too many recent restarts",
                "confidence": confidence * 0.8,
                "original_action": action
            }
        
        # For new services, be more careful
        if action == "restart_service" and service_uptime < 1:
            return {
                "action": "monitor",
                "reason": "Service is new, monitoring first",
                "confidence": confidence * 0.6,
                "original_action": action
            }
        
        # Only take action if confidence is high enough
        if confidence < 0.6:
            return {
                "action": "monitor",
                "reason": f"Confidence too low ({confidence:.2f})",
                "confidence": confidence,
                "original_action": action
            }
        
        return {
            "action": action,
            "reason": analysis.get("root_cause", "Unknown"),
            "confidence": confidence,
            "pattern": analysis.get("pattern_matched")
        }
    
    def learn_from_incident(self, incident: Dict, action_taken: str, result: Dict):
        """Learn from incident outcomes to improve future decisions"""
        # Store incident in memory for pattern learning
        # In production, this would update the patterns database
        logger.info(f"Learning from incident: {incident.get('id')}, action: {action_taken}, success: {result.get('success')}")
        
        # Update confidence based on result
        if result.get('success'):
            # Action worked, increase confidence for this pattern
            logger.info("Action successful - reinforcing pattern")
        else:
            # Action failed, adjust for next time
            logger.info("Action failed - will try different approach next time")

# Global instance
local_ai = LocalAI()