"""
Prediction Agent — Equipment failure prediction, RUL estimation, 
and early warning generation.
"""
import json
import os
from backend.config import settings
from backend.services.rul_predictor import rul_predictor
from backend.services.anomaly_detector import anomaly_detector
from backend.services.llm_client import llm_client


class PredictionAgent:
    """Predicts equipment failures and provides early warnings."""

    def __init__(self):
        self.equipment_data = []
        self.sensor_data = {}
        self._load_data()

    def _load_data(self):
        eq_path = os.path.join(settings.DATA_DIR, "equipment.json")
        sensor_path = os.path.join(settings.DATA_DIR, "sensor_data_full.json")

        if os.path.exists(eq_path):
            with open(eq_path, "r") as f:
                self.equipment_data = json.load(f)

        if os.path.exists(sensor_path):
            with open(sensor_path, "r") as f:
                self.sensor_data = json.load(f)

    def _get_equipment(self, equipment_id: str) -> dict:
        if not self.equipment_data:
            self._load_data()
        return next((e for e in self.equipment_data if e["id"] == equipment_id), {})

    async def predict_equipment(self, equipment_id: str) -> dict:
        """Get full prediction for a single equipment."""
        if not self.equipment_data or not self.sensor_data:
            self._load_data()
        eq = self._get_equipment(equipment_id)
        readings = self.sensor_data.get(equipment_id, [])

        if not eq or not readings:
            return {"error": f"No data found for equipment {equipment_id}"}

        # RUL prediction
        rul_result = rul_predictor.predict_rul(
            readings, eq.get("type", ""), eq.get("rated_hours", 50000)
        )
        rul_result["risk_level"] = rul_predictor.get_risk_level(rul_result)

        # Anomaly detection
        anomaly_summary = anomaly_detector.get_equipment_anomaly_summary(
            equipment_id, readings[-42:], eq.get("type")
        )

        # Generate AI interpretation
        interpretation = await self._interpret_prediction(eq, rul_result, anomaly_summary)

        return {
            "equipment_id": equipment_id,
            "equipment_name": eq.get("name", ""),
            "equipment_type": eq.get("type", ""),
            "area": eq.get("area", ""),
            "rul": rul_result,
            "anomaly_summary": anomaly_summary,
            "interpretation": interpretation,
            "agent": "prediction"
        }

    async def get_fleet_predictions(self) -> list:
        """Get predictions for all equipment, sorted by risk."""
        if not self.equipment_data or not self.sensor_data:
            self._load_data()
        predictions = []
        for eq in self.equipment_data:
            readings = self.sensor_data.get(eq["id"], [])
            if not readings:
                continue

            rul_result = rul_predictor.predict_rul(
                readings, eq.get("type", ""), eq.get("rated_hours", 50000)
            )
            rul_result["risk_level"] = rul_predictor.get_risk_level(rul_result)

            predictions.append({
                "equipment_id": eq["id"],
                "equipment_name": eq["name"],
                "area": eq["area"],
                "type": eq["type"],
                "criticality": eq.get("criticality", "medium"),
                "current_health": rul_result["current_health"],
                "rul_days": rul_result["rul_days"],
                "risk_level": rul_result["risk_level"],
                "health_trend": rul_result["health_trend"],
                "failure_probability_30d": rul_result["failure_probability_30d"],
            })

        # Sort by risk (critical first)
        risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}
        predictions.sort(key=lambda p: (risk_order.get(p["risk_level"], 5), -(p.get("failure_probability_30d", 0))))

        return predictions

    async def get_early_warnings(self) -> list:
        """Generate early warnings for equipment at risk."""
        predictions = await self.get_fleet_predictions()
        warnings = []

        for p in predictions:
            if p["risk_level"] in ["critical", "high"]:
                warnings.append({
                    "equipment_id": p["equipment_id"],
                    "equipment_name": p["equipment_name"],
                    "area": p["area"],
                    "risk_level": p["risk_level"],
                    "rul_days": p["rul_days"],
                    "current_health": p["current_health"],
                    "failure_probability_30d": p["failure_probability_30d"],
                    "health_trend": p["health_trend"],
                    "warning": f"{p['equipment_name']} showing {p['health_trend'].replace('_', ' ')} — "
                               f"estimated {p['rul_days']:.0f} days remaining, "
                               f"{p['failure_probability_30d']*100:.0f}% failure probability in 30 days"
                })

        return warnings

    async def _interpret_prediction(self, equipment: dict, rul: dict, anomalies: dict) -> str:
        """Use LLM to generate human-readable interpretation of predictions."""
        prompt = f"""You are a predictive maintenance expert for a steel plant. Interpret these predictions for a maintenance engineer.

EQUIPMENT: {equipment.get('name', '')} ({equipment.get('type', '')})
Area: {equipment.get('area', '')} | Criticality: {equipment.get('criticality', '')}

PREDICTIONS:
- Current Health Index: {rul.get('current_health', 'N/A')}/100
- Remaining Useful Life: {rul.get('rul_days', 'N/A')} days
- Health Trend: {rul.get('health_trend', 'N/A')}
- Degradation Rate: {rul.get('degradation_rate', 0)} health points/day
- 30-day Failure Probability: {rul.get('failure_probability_30d', 0)*100:.1f}%
- Risk Level: {rul.get('risk_level', 'N/A')}

ANOMALIES DETECTED:
- Count: {anomalies.get('anomaly_count', 0)}
- Max Severity: {anomalies.get('max_severity', 'none')}
- Trend: {anomalies.get('trend', 'stable')}

Provide a concise 3-4 sentence interpretation covering:
1. Current equipment condition
2. Expected trajectory
3. Recommended action priority
Be specific and actionable."""

        response_text = llm_client.generate_content("flash", prompt)
        return response_text


# Singleton
prediction_agent = PredictionAgent()
