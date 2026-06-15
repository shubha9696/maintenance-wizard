"""Reports router — Report generation and retrieval."""
from fastapi import APIRouter
from backend.models.schemas import ReportRequest
from backend.agents.report_agent import report_agent

router = APIRouter(prefix="/api/reports", tags=["Reports"])

# In-memory report store
generated_reports = []


@router.post("/generate")
async def generate_report(request: ReportRequest):
    """Generate a maintenance report."""
    result = await report_agent.generate_report(
        report_type=request.report_type,
        equipment_id=request.equipment_id,
        area=request.area
    )
    generated_reports.append(result)
    return result


@router.get("")
async def list_reports():
    """List all generated reports."""
    return {"reports": generated_reports, "total": len(generated_reports)}


@router.get("/types")
async def report_types():
    """List available report types."""
    return {
        "types": [
            {"id": "maintenance_summary", "name": "Maintenance Summary", "description": "Overview of recent maintenance activities"},
            {"id": "alert_summary", "name": "Alert Summary", "description": "Current anomaly alerts and recommended actions"},
            {"id": "equipment_health", "name": "Equipment Health Card", "description": "Detailed health report for specific equipment"},
            {"id": "failure_analysis", "name": "Failure Analysis", "description": "Analysis of failure patterns and root causes"}
        ]
    }
