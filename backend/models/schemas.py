"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class FeedbackType(str, Enum):
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"

class EquipmentArea(str, Enum):
    BLAST_FURNACE = "Blast Furnace"
    STEEL_MELTING_SHOP = "Steel Melting Shop"
    ROLLING_MILL = "Rolling Mill"
    COKE_OVEN = "Coke Oven"
    SINTER_PLANT = "Sinter Plant"
    POWER_PLANT = "Power Plant"


# ── Equipment ──────────────────────────────────────────
class SensorReading(BaseModel):
    timestamp: str
    vibration: float
    temperature: float
    pressure: float
    current: float

class Equipment(BaseModel):
    id: str
    name: str
    area: str
    type: str
    criticality: str
    status: str
    health_score: float
    last_maintenance: str
    sensor_readings: Optional[List[SensorReading]] = None

class EquipmentDetail(Equipment):
    rul_days: Optional[float] = None
    rul_confidence: Optional[float] = None
    risk_level: Optional[str] = None
    maintenance_history: Optional[List[Dict[str, Any]]] = None
    spare_parts: Optional[List[Dict[str, Any]]] = None


# ── Chat ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    equipment_id: Optional[str] = None

class SourceReference(BaseModel):
    document: str
    section: str
    relevance_score: float
    content: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent_used: str
    sources: Optional[List[SourceReference]] = None
    risk_level: Optional[str] = None
    equipment_id: Optional[str] = None
    recommendations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ── Alerts ─────────────────────────────────────────────
class Alert(BaseModel):
    id: str
    equipment_id: str
    equipment_name: str
    area: str
    type: str
    severity: str
    message: str
    timestamp: str
    status: str = "active"
    sensor_values: Optional[Dict[str, float]] = None

class AlertSummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    alerts: List[Alert]


# ── Reports ────────────────────────────────────────────
class ReportRequest(BaseModel):
    report_type: str = "maintenance_summary"
    equipment_id: Optional[str] = None
    area: Optional[str] = None
    date_range: Optional[str] = None

class Report(BaseModel):
    id: str
    title: str
    type: str
    generated_at: str
    content: str
    summary: str
    equipment_covered: List[str]


# ── Feedback ───────────────────────────────────────────
class FeedbackRequest(BaseModel):
    session_id: str
    message_index: int
    feedback_type: str
    comment: Optional[str] = None
    correction: Optional[str] = None

class FeedbackStats(BaseModel):
    total_feedback: int
    positive: int
    negative: int
    improvement_rate: float
    recent_feedback: List[Dict[str, Any]]


# ── Dashboard ──────────────────────────────────────────
class DashboardStats(BaseModel):
    total_equipment: int
    healthy_count: int
    warning_count: int
    critical_count: int
    active_alerts: int
    avg_health_score: float
    maintenance_due: int
    recent_activities: List[Dict[str, Any]]
