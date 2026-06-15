"""
RUL (Remaining Useful Life) Predictor — Estimates equipment degradation
and remaining service life using trend analysis and health indexing.
"""
import json
import os
import numpy as np
from datetime import datetime, timedelta
from backend.config import settings


class RULPredictor:
    """Predicts Remaining Useful Life using sensor trend analysis and health indexing."""

    def __init__(self):
        self.sensor_ranges = {}
        self.equipment_data = {}
        self._load_data()

    def _load_data(self):
        ranges_path = os.path.join(settings.DATA_DIR, "sensor_ranges.json")
        if os.path.exists(ranges_path):
            with open(ranges_path, "r") as f:
                self.sensor_ranges = json.load(f)

    def compute_health_index(self, readings: list, equipment_type: str) -> list:
        """Compute a 0-100 health index for each reading based on sensor deviations."""
        if equipment_type not in self.sensor_ranges:
            return [{"timestamp": r.get("timestamp"), "health_index": 80.0} for r in readings]

        ranges = self.sensor_ranges[equipment_type]
        health_series = []

        for r in readings:
            scores = []
            for sensor in ["vibration", "temperature", "pressure", "current"]:
                low, high = ranges.get(sensor, (0, 0))
                if high == low:
                    continue
                val = r.get(sensor, (low + high) / 2)
                mid = (low + high) / 2
                rng = (high - low) / 2
                if rng == 0:
                    continue
                deviation = abs(val - mid) / rng
                # Score: 100 when at midpoint, decreasing as deviation increases
                score = max(0, 100 - deviation * 40)
                scores.append(score)

            health = sum(scores) / len(scores) if scores else 80
            health_series.append({
                "timestamp": r.get("timestamp"),
                "health_index": round(max(0, min(100, health)), 1)
            })

        return health_series

    def predict_rul(self, readings: list, equipment_type: str, rated_hours: int = 50000) -> dict:
        """
        Predict Remaining Useful Life based on health index trend.
        Uses linear regression on health index to estimate when it will reach failure threshold.
        """
        health_series = self.compute_health_index(readings, equipment_type)

        if len(health_series) < 10:
            return {
                "rul_days": None,
                "confidence": 0.0,
                "health_trend": "insufficient_data",
                "current_health": health_series[-1]["health_index"] if health_series else 80,
                "degradation_rate": 0,
                "failure_probability_30d": 0,
            }

        # Extract health values
        health_values = np.array([h["health_index"] for h in health_series])
        x = np.arange(len(health_values))

        # Linear regression for trend
        coeffs = np.polyfit(x, health_values, 1)
        slope = coeffs[0]  # Health change per reading interval

        current_health = health_values[-1]

        # Failure threshold (health index below which equipment is considered failed)
        failure_threshold = 30.0

        # Time per reading interval (assuming 4-hour intervals based on our data)
        hours_per_interval = 4.0
        days_per_interval = hours_per_interval / 24.0

        if slope >= 0:
            # Health is stable or improving
            rul_days = max(180, rated_hours / 24)  # Use rated life
            trend = "stable" if abs(slope) < 0.01 else "improving"
            failure_prob = max(0, (100 - current_health) / 200)
        else:
            # Health is declining — extrapolate to failure threshold
            intervals_to_failure = (current_health - failure_threshold) / abs(slope)
            rul_days = intervals_to_failure * days_per_interval

            if rul_days < 0:
                rul_days = 0
                trend = "critical_degradation"
            elif rul_days < 7:
                trend = "rapid_degradation"
            elif rul_days < 30:
                trend = "accelerating_degradation"
            else:
                trend = "gradual_degradation"

            # Failure probability in next 30 days
            projected_health_30d = current_health + slope * (30 / days_per_interval)
            if projected_health_30d < failure_threshold:
                failure_prob = min(0.95, (failure_threshold - projected_health_30d) / failure_threshold + 0.5)
            else:
                failure_prob = max(0.05, (failure_threshold / projected_health_30d) * 0.3)

        # Confidence based on data quality and R-squared
        residuals = health_values - np.polyval(coeffs, x)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((health_values - np.mean(health_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        confidence = max(0.3, min(0.95, r_squared * 0.7 + 0.3))

        # Degradation rate per day
        degradation_rate = abs(slope) / days_per_interval if slope < 0 else 0

        return {
            "rul_days": round(max(0, rul_days), 1),
            "confidence": round(confidence, 2),
            "health_trend": trend,
            "current_health": round(current_health, 1),
            "degradation_rate": round(degradation_rate, 3),
            "failure_probability_30d": round(min(1.0, failure_prob), 2),
            "health_history": health_series[-42:],  # Last 7 days
            "slope": round(float(slope), 6),
        }

    def get_risk_level(self, rul_result: dict) -> str:
        """Classify risk level based on RUL prediction."""
        rul = rul_result.get("rul_days")
        health = rul_result.get("current_health", 80)
        failure_prob = rul_result.get("failure_probability_30d", 0)

        if rul is None:
            return "unknown"
        if rul < 7 or health < 35 or failure_prob > 0.7:
            return "critical"
        if rul < 30 or health < 50 or failure_prob > 0.4:
            return "high"
        if rul < 90 or health < 65 or failure_prob > 0.2:
            return "medium"
        return "low"

    def batch_predict(self, sensor_data: dict, equipment_list: list) -> dict:
        """Predict RUL for all equipment."""
        results = {}
        eq_map = {eq["id"]: eq for eq in equipment_list}

        for eq_id, readings in sensor_data.items():
            eq = eq_map.get(eq_id, {})
            eq_type = eq.get("type", "Unknown")
            rated_hours = eq.get("rated_hours", 50000)

            rul_result = self.predict_rul(readings, eq_type, rated_hours)
            rul_result["risk_level"] = self.get_risk_level(rul_result)
            rul_result["equipment_id"] = eq_id
            results[eq_id] = rul_result

        return results


# Singleton
rul_predictor = RULPredictor()
