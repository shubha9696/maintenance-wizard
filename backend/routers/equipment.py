"""Equipment router — Equipment data, health, sensor readings, and predictions."""
import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import settings
from backend.services.rul_predictor import rul_predictor
from backend.services.anomaly_detector import anomaly_detector

router = APIRouter(prefix="/api/equipment", tags=["Equipment"])



_json_cache = {}


def _load_json(filename):
    if filename not in _json_cache:
        path = os.path.join(settings.DATA_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _json_cache[filename] = json.load(f)
        else:
            _json_cache[filename] = []
    # Return a copy to prevent in-place modifications modifying the cache
    data = _json_cache[filename]
    if isinstance(data, list):
        return list(data)
    elif isinstance(data, dict):
        return dict(data)
    return data


@router.get("")
async def list_equipment():
    """List all equipment with health scores."""
    equipment = _load_json("equipment.json")
    return {"equipment": equipment, "total": len(equipment)}


@router.get("/dashboard")
async def dashboard_stats():
    """Get dashboard statistics."""
    equipment = _load_json("equipment.json")
    logs = _load_json("maintenance_logs.json")

    healthy = sum(1 for e in equipment if e.get("health_score", 0) >= 80)
    warning = sum(1 for e in equipment if 50 <= e.get("health_score", 0) < 80)
    critical = sum(1 for e in equipment if e.get("health_score", 0) < 50)
    health_scores = [e.get("health_score", 80) for e in equipment]
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 80

    # Count active alerts (equipment with risk high or critical)
    active_alerts = sum(1 for e in equipment if e.get("risk_level") in ["high", "critical"])

    # Maintenance due (health < 70 or critical equipment with health < 80)
    maint_due = sum(1 for e in equipment if e.get("health_score", 80) < 70 or
                    (e.get("criticality") == "critical" and e.get("health_score", 80) < 80))

    # Recent activities
    recent = logs[:10] if logs else []

    # Area-wise health
    areas = {}
    for e in equipment:
        area = e.get("area", "Unknown")
        if area not in areas:
            areas[area] = {"total": 0, "health_sum": 0, "critical_count": 0}
        areas[area]["total"] += 1
        areas[area]["health_sum"] += e.get("health_score", 80)
        if e.get("risk_level") in ["high", "critical"]:
            areas[area]["critical_count"] += 1

    area_stats = [
        {
            "area": area,
            "avg_health": round(data["health_sum"] / data["total"], 1),
            "equipment_count": data["total"],
            "critical_count": data["critical_count"]
        }
        for area, data in areas.items()
    ]

    return {
        "total_equipment": len(equipment),
        "healthy_count": healthy,
        "warning_count": warning,
        "critical_count": critical,
        "active_alerts": active_alerts,
        "avg_health_score": round(avg_health, 1),
        "maintenance_due": maint_due,
        "recent_activities": recent,
        "area_stats": area_stats
    }


_analytics_cache = None


async def warm_analytics_cache():
    """Warm up the analytics cache on startup."""
    global _analytics_cache
    if _analytics_cache is None:
        await fleet_analytics()


@router.get("/analytics")
async def fleet_analytics():
    """Aggregated predictive analytics for the entire fleet."""
    global _analytics_cache
    if _analytics_cache is not None:
        return _analytics_cache

    equipment = _load_json("equipment.json")
    full_sensor = _load_json("sensor_data_full.json")

    risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    failure_timeline = []
    degradation_board = []
    anomaly_trends = []

    total_prevented_downtime_hrs = 0
    total_maintenance_cost = 0

    for eq in equipment:
        eq_id = eq["id"]
        eq_type = eq.get("type", "")
        readings = full_sensor.get(eq_id, [])

        # RUL prediction
        rul_result = rul_predictor.predict_rul(readings, eq_type, eq.get("rated_hours", 50000))
        risk = rul_predictor.get_risk_level(rul_result)
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

        rul_days = rul_result.get("rul_days") or 999
        failure_timeline.append({
            "id": eq_id,
            "name": eq.get("name", eq_id),
            "area": eq.get("area", ""),
            "rul_days": round(rul_days, 1),
            "health": rul_result.get("current_health", 80),
            "risk": risk,
            "failure_prob_30d": rul_result.get("failure_probability_30d", 0),
        })

        degradation_board.append({
            "id": eq_id,
            "name": eq.get("name", eq_id),
            "area": eq.get("area", ""),
            "health": rul_result.get("current_health", 80),
            "degradation_rate": rul_result.get("degradation_rate", 0),
            "trend": rul_result.get("health_trend", "stable"),
            "failure_prob_30d": rul_result.get("failure_probability_30d", 0),
            "rul_days": round(rul_days, 1),
        })

        # Anomaly summary (last 7 days = 42 readings at 4h intervals)
        anomaly_summary = anomaly_detector.get_equipment_anomaly_summary(
            eq_id, readings[-42:], eq_type
        )
        anomaly_trends.append({
            "id": eq_id,
            "name": eq.get("name", eq_id),
            "anomaly_count": anomaly_summary.get("anomaly_count", 0),
            "max_severity": anomaly_summary.get("max_severity", "none"),
            "trend": anomaly_summary.get("trend", "stable"),
        })

        # ROI: if risk is high/critical, we "prevented" unplanned downtime
        if risk in ("critical", "high"):
            total_prevented_downtime_hrs += 12  # average per incident
            total_maintenance_cost += 2500  # average planned maintenance cost

    # Sort failure timeline by rul_days ascending (most urgent first)
    failure_timeline.sort(key=lambda x: x["rul_days"])

    # Sort degradation leaderboard by degradation_rate descending
    degradation_board.sort(key=lambda x: x["degradation_rate"], reverse=True)

    roi = {
        "prevented_downtime_hours": total_prevented_downtime_hrs,
        "unplanned_cost_per_hour": 10000,
        "savings_from_prevention": total_prevented_downtime_hrs * 10000,
        "planned_maintenance_cost": total_maintenance_cost,
        "net_savings": (total_prevented_downtime_hrs * 10000) - total_maintenance_cost,
    }

    _analytics_cache = {
        "risk_distribution": risk_counts,
        "failure_timeline": failure_timeline[:25],
        "degradation_leaderboard": degradation_board[:15],
        "anomaly_trends": anomaly_trends,
        "roi": roi,
        "total_equipment": len(equipment),
    }

    return _analytics_cache



@router.get("/spare-parts/all")
async def get_all_spare_parts():
    """Get all spare parts inventory from JSON."""
    spares = _load_json("spare_parts.json")
    return spares


@router.get("/{equipment_id}")
async def get_equipment(equipment_id: str):
    """Get detailed equipment information with sensor data."""
    equipment = _load_json("equipment.json")
    eq = next((e for e in equipment if e["id"] == equipment_id), None)
    if not eq:
        raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")

    # Get sensor data
    sensor_data = _load_json("sensor_data.json")
    readings = sensor_data.get(equipment_id, [])

    # Get maintenance history
    logs = _load_json("maintenance_logs.json")
    history = [l for l in logs if l["equipment_id"] == equipment_id][:20]

    # Get spare parts
    spares = _load_json("spare_parts.json")
    eq_spares = spares.get(eq.get("type", ""), [])

    return {
        **eq,
        "sensor_readings": readings,
        "maintenance_history": history,
        "spare_parts": eq_spares
    }


@router.get("/{equipment_id}/health")
async def get_equipment_health(equipment_id: str):
    """Get equipment health prediction and RUL."""
    equipment = _load_json("equipment.json")
    eq = next((e for e in equipment if e["id"] == equipment_id), None)
    if not eq:
        raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")

    # Full sensor data for prediction
    full_sensor = _load_json("sensor_data_full.json")
    readings = full_sensor.get(equipment_id, [])

    rul_result = rul_predictor.predict_rul(readings, eq.get("type", ""), eq.get("rated_hours", 50000))
    rul_result["risk_level"] = rul_predictor.get_risk_level(rul_result)

    anomaly_summary = anomaly_detector.get_equipment_anomaly_summary(
        equipment_id, readings[-42:], eq.get("type")
    )

    return {
        "equipment_id": equipment_id,
        "equipment_name": eq.get("name", ""),
        "rul": rul_result,
        "anomalies": anomaly_summary
    }


class TelemetryAnalysisRequest(BaseModel):
    vibration: float
    temperature: float
    pressure: float
    current: float


@router.post("/{equipment_id}/analyze")
async def analyze_telemetry(equipment_id: str, data: TelemetryAnalysisRequest):
    """Analyze a single telemetry reading for anomalies on-the-fly."""
    equipment = _load_json("equipment.json")
    eq = next((e for e in equipment if e["id"] == equipment_id), None)
    if not eq:
        raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")

    reading = {
        "timestamp": datetime.now().isoformat(),
        "vibration": data.vibration,
        "temperature": data.temperature,
        "pressure": data.pressure,
        "current": data.current
    }

    anomaly_details = anomaly_detector._check_reading(equipment_id, reading, eq.get("type"))

    if anomaly_details:
        return {
            "is_anomaly": True,
            "severity": anomaly_details["severity"],
            "severity_score": anomaly_details["severity_score"],
            "issues": anomaly_details["issues"]
        }
    else:
        return {
            "is_anomaly": False,
            "severity": "none",
            "severity_score": 0.0,
            "issues": []
        }

