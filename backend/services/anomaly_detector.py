"""
Anomaly Detection Service — Real-time anomaly detection for equipment sensors.
Uses Isolation Forest + statistical methods for multivariate anomaly detection.
"""
import json
import os
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from backend.config import settings


class AnomalyDetector:
    """Detects anomalies in equipment sensor data using multiple methods."""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.sensor_ranges = {}
        self._load_sensor_ranges()

    def _load_sensor_ranges(self):
        ranges_path = os.path.join(settings.DATA_DIR, "sensor_ranges.json")
        if os.path.exists(ranges_path):
            with open(ranges_path, "r") as f:
                self.sensor_ranges = json.load(f)

    def train_models(self, sensor_data: dict, equipment_list: list):
        """Train Isolation Forest models per equipment using historical data."""
        eq_type_map = {eq["id"]: eq["type"] for eq in equipment_list}

        for eq_id, readings in sensor_data.items():
            if len(readings) < 50:
                continue

            features = np.array([
                [r["vibration"], r["temperature"], r["pressure"], r["current"]]
                for r in readings
            ])

            # Remove zero-variance columns
            valid_cols = features.std(axis=0) > 0.001
            if not valid_cols.any():
                continue

            features_clean = features[:, valid_cols]

            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_clean)

            model = IsolationForest(
                n_estimators=100,
                contamination=0.05,
                random_state=42
            )
            model.fit(features_scaled)

            self.models[eq_id] = {"model": model, "valid_cols": valid_cols}
            self.scalers[eq_id] = scaler

    def detect_anomalies(self, equipment_id: str, readings: list, equipment_type: str = None) -> list:
        """Detect anomalies in recent sensor readings for an equipment."""
        alerts = []

        for reading in readings:
            anomaly_details = self._check_reading(equipment_id, reading, equipment_type)
            if anomaly_details:
                alerts.append(anomaly_details)

        return alerts

    def _check_reading(self, equipment_id: str, reading: dict, equipment_type: str = None) -> dict:
        """Check a single reading for anomalies using multiple methods."""
        if not self.sensor_ranges:
            self._load_sensor_ranges()

        issues = []
        severity_score = 0
        sensor_values = {
            "vibration": reading.get("vibration", 0),
            "temperature": reading.get("temperature", 0),
            "pressure": reading.get("pressure", 0),
            "current": reading.get("current", 0),
        }

        # Method 1: Threshold-based detection
        if equipment_type and equipment_type in self.sensor_ranges:
            ranges = self.sensor_ranges[equipment_type]
            for sensor, value in sensor_values.items():
                if sensor not in ranges:
                    continue
                low, high = ranges[sensor]
                if high == low == 0:
                    continue

                margin = (high - low) * 0.15
                if value > high + margin:
                    excess_pct = ((value - high) / (high - low)) * 100
                    issues.append({
                        "sensor": sensor,
                        "type": "threshold_exceeded",
                        "value": value,
                        "limit": high,
                        "excess_percent": round(excess_pct, 1),
                        "message": f"{sensor.title()} ({value:.1f}) exceeds upper limit ({high:.1f}) by {excess_pct:.0f}%"
                    })
                    severity_score += min(excess_pct / 20, 4)
                elif value < low - margin and low > 0:
                    deficit_pct = ((low - value) / (high - low)) * 100
                    issues.append({
                        "sensor": sensor,
                        "type": "below_threshold",
                        "value": value,
                        "limit": low,
                        "deficit_percent": round(deficit_pct, 1),
                        "message": f"{sensor.title()} ({value:.1f}) below lower limit ({low:.1f}) by {deficit_pct:.0f}%"
                    })
                    severity_score += min(deficit_pct / 25, 3)

        # Method 2: Isolation Forest detection
        if equipment_id in self.models:
            model_info = self.models[equipment_id]
            scaler = self.scalers[equipment_id]
            features = np.array([[
                sensor_values["vibration"],
                sensor_values["temperature"],
                sensor_values["pressure"],
                sensor_values["current"]
            ]])
            features_clean = features[:, model_info["valid_cols"]]
            features_scaled = scaler.transform(features_clean)

            prediction = model_info["model"].predict(features_scaled)
            anomaly_score = model_info["model"].score_samples(features_scaled)[0]

            if prediction[0] == -1:
                issues.append({
                    "sensor": "multivariate",
                    "type": "isolation_forest_anomaly",
                    "anomaly_score": round(float(anomaly_score), 4),
                    "message": f"Multivariate anomaly detected (score: {anomaly_score:.4f})"
                })
                severity_score += 2

        if not issues:
            return None

        # Determine severity
        if severity_score >= 6:
            severity = "critical"
        elif severity_score >= 4:
            severity = "high"
        elif severity_score >= 2:
            severity = "medium"
        else:
            severity = "low"

        return {
            "equipment_id": equipment_id,
            "timestamp": reading.get("timestamp", datetime.now().isoformat()),
            "severity": severity,
            "severity_score": round(severity_score, 2),
            "issues": issues,
            "sensor_values": sensor_values
        }

    def get_equipment_anomaly_summary(self, equipment_id: str, readings: list, equipment_type: str = None) -> dict:
        """Get anomaly summary for an equipment over recent readings."""
        anomalies = self.detect_anomalies(equipment_id, readings, equipment_type)

        if not anomalies:
            return {
                "equipment_id": equipment_id,
                "anomaly_count": 0,
                "max_severity": "none",
                "trend": "stable",
                "anomalies": []
            }

        severities = [a["severity"] for a in anomalies]
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        max_sev = max(severities, key=lambda s: severity_order.get(s, 0))

        # Trend analysis — are anomalies increasing?
        first_half = anomalies[:len(anomalies)//2]
        second_half = anomalies[len(anomalies)//2:]
        trend = "worsening" if len(second_half) > len(first_half) * 1.3 else \
                "improving" if len(second_half) < len(first_half) * 0.7 else "stable"

        return {
            "equipment_id": equipment_id,
            "anomaly_count": len(anomalies),
            "max_severity": max_sev,
            "trend": trend,
            "anomalies": anomalies[-10:]  # Last 10 anomalies
        }


# Singleton
anomaly_detector = AnomalyDetector()
