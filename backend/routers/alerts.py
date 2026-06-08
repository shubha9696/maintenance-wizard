"""Alerts router — Anomaly alerts and notifications."""
import json
import os
from fastapi import APIRouter
from backend.config import settings
from backend.services.anomaly_detector import anomaly_detector

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


_json_cache = {}


def _load_json(filename):
    if filename not in _json_cache:
        path = os.path.join(settings.DATA_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _json_cache[filename] = json.load(f)
        else:
            _json_cache[filename] = {} if filename == "sensor_data.json" else []
    # Return a copy to prevent in-place modifications modifying the cache
    data = _json_cache[filename]
    if isinstance(data, list):
        return list(data)
    elif isinstance(data, dict):
        return dict(data)
    return data


@router.get("")
async def get_alerts():
    """Get all active anomaly alerts."""
    equipment = _load_json("equipment.json")
    sensor_data = _load_json("sensor_data.json")
    alerts = []
    alert_id = 0

    for eq in equipment:
        eq_id = eq["id"]
        readings = sensor_data.get(eq_id, [])
        if not readings:
            continue

        # Check last few readings for anomalies
        recent_readings = readings[-6:]
        detected = anomaly_detector.detect_anomalies(eq_id, recent_readings, eq.get("type"))

        for anomaly in detected:
            alert_id += 1
            primary_issue = anomaly["issues"][0] if anomaly["issues"] else {}
            alerts.append({
                "id": f"ALT-{alert_id:04d}",
                "equipment_id": eq_id,
                "equipment_name": eq.get("name", ""),
                "area": eq.get("area", ""),
                "type": primary_issue.get("type", "anomaly"),
                "severity": anomaly["severity"],
                "message": primary_issue.get("message", "Anomaly detected"),
                "timestamp": anomaly.get("timestamp", ""),
                "status": "active",
                "sensor_values": anomaly.get("sensor_values", {})
            })

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda a: severity_order.get(a["severity"], 4))

    return {"alerts": alerts, "total": len(alerts)}


@router.get("/summary")
async def alert_summary():
    """Get alert dashboard summary."""
    result = await get_alerts()
    alerts = result["alerts"]

    critical = sum(1 for a in alerts if a["severity"] == "critical")
    high = sum(1 for a in alerts if a["severity"] == "high")
    medium = sum(1 for a in alerts if a["severity"] == "medium")
    low = sum(1 for a in alerts if a["severity"] == "low")

    # Group by area
    by_area = {}
    for a in alerts:
        area = a.get("area", "Unknown")
        by_area[area] = by_area.get(area, 0) + 1

    return {
        "total": len(alerts),
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "by_area": by_area,
        "alerts": alerts[:20]  # Top 20 alerts
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    return {"status": "acknowledged", "alert_id": alert_id}
