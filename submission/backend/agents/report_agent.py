"""
Report Agent — Generates structured maintenance reports, alert summaries,
and equipment health cards.
"""
import json
import os
from datetime import datetime
from backend.config import settings
from backend.services.llm_client import llm_client


class ReportAgent:
    """Generates structured maintenance reports and summaries."""

    def __init__(self):
        self.equipment_data = []
        self.maintenance_logs = []
        self.failure_reports = []
        self._load_data()

    def _load_data(self):
        for attr, filename in [
            ("equipment_data", "equipment.json"),
            ("maintenance_logs", "maintenance_logs.json"),
            ("failure_reports", "failure_reports.json")
        ]:
            path = os.path.join(settings.DATA_DIR, filename)
            if os.path.exists(path):
                with open(path, "r") as f:
                    setattr(self, attr, json.load(f))

    async def generate_report(self, report_type: str = "maintenance_summary",
                               equipment_id: str = None, area: str = None) -> dict:
        """Generate a structured maintenance report."""
        if report_type == "maintenance_summary":
            return await self._maintenance_summary_report(equipment_id, area)
        elif report_type == "alert_summary":
            return await self._alert_summary_report(area)
        elif report_type == "equipment_health":
            return await self._equipment_health_report(equipment_id)
        elif report_type == "failure_analysis":
            return await self._failure_analysis_report(equipment_id, area)
        else:
            return await self._maintenance_summary_report(equipment_id, area)

    async def _maintenance_summary_report(self, equipment_id: str = None, area: str = None) -> dict:
        """Generate maintenance activity summary report."""
        logs = self.maintenance_logs
        if equipment_id:
            logs = [l for l in logs if l["equipment_id"] == equipment_id]
        if area:
            logs = [l for l in logs if l["area"] == area]

        recent_logs = logs[:30]

        # Statistics
        total_downtime = sum(l.get("downtime_hours", 0) for l in recent_logs)
        action_counts = {}
        for l in recent_logs:
            at = l.get("action_type", "Unknown")
            action_counts[at] = action_counts.get(at, 0) + 1

        breakdown_count = sum(1 for l in recent_logs if l.get("action_type") in ["Breakdown Repair", "Emergency Repair"])

        # LLM-enhanced summary
        log_summary = "\n".join([
            f"- [{l['date']}] {l['equipment_name']}: {l['action_type']} — {l.get('failure_mode', 'N/A')} (Downtime: {l.get('downtime_hours', 0)}h)"
            for l in recent_logs[:15]
        ])

        prompt = f"""Generate a professional maintenance summary report based on this data:

PERIOD: Recent maintenance activities
SCOPE: {f'Equipment {equipment_id}' if equipment_id else f'Area: {area}' if area else 'All Plant Equipment'}

STATISTICS:
- Total Activities: {len(recent_logs)}
- Total Downtime: {total_downtime:.1f} hours
- Breakdown/Emergency Repairs: {breakdown_count}
- Activity Breakdown: {json.dumps(action_counts)}

RECENT ACTIVITIES:
{log_summary}

Generate a structured report with:
1. **Executive Summary** (2-3 sentences)
2. **Key Metrics** (bullet points)
3. **Notable Issues** (any concerning patterns)
4. **Recommendations** (3-5 actionable items)
5. **Maintenance Efficiency Assessment**

Format with markdown headers."""

        response_text = llm_client.generate_content("flash", prompt)

        return {
            "id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"Maintenance Summary Report — {datetime.now().strftime('%B %Y')}",
            "type": "maintenance_summary",
            "generated_at": datetime.now().isoformat(),
            "content": response_text,
            "summary": f"{len(recent_logs)} activities, {total_downtime:.0f}h downtime, {breakdown_count} breakdowns",
            "equipment_covered": list(set(l["equipment_id"] for l in recent_logs)),
            "statistics": {
                "total_activities": len(recent_logs),
                "total_downtime_hours": round(total_downtime, 1),
                "breakdown_count": breakdown_count,
                "action_distribution": action_counts
            }
        }

    async def _alert_summary_report(self, area: str = None) -> dict:
        """Generate alert summary report."""
        equipment = self.equipment_data
        if area:
            equipment = [e for e in equipment if e.get("area") == area]

        critical = [e for e in equipment if e.get("risk_level") == "critical"]
        high = [e for e in equipment if e.get("risk_level") == "high"]
        warning = [e for e in equipment if e.get("status") in ["warning", "degraded"]]

        prompt = f"""Generate a concise alert summary report for a steel plant maintenance team:

CRITICAL EQUIPMENT ({len(critical)}):
{chr(10).join([f'- {e["name"]} (Health: {e.get("health_score", "N/A")})' for e in critical]) or 'None'}

HIGH RISK EQUIPMENT ({len(high)}):
{chr(10).join([f'- {e["name"]} (Health: {e.get("health_score", "N/A")})' for e in high]) or 'None'}

WARNING STATUS ({len(warning)}):
{chr(10).join([f'- {e["name"]} (Health: {e.get("health_score", "N/A")})' for e in warning]) or 'None'}

Generate a structured alert report with:
1. **Alert Overview** — current alert status
2. **Critical Alerts** — equipment requiring immediate attention
3. **Action Items** — prioritized list of actions
4. **Escalation Notes** — what should be escalated to management"""

        response_text = llm_client.generate_content("flash", prompt)

        return {
            "id": f"ALR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"Alert Summary Report — {datetime.now().strftime('%d %B %Y')}",
            "type": "alert_summary",
            "generated_at": datetime.now().isoformat(),
            "content": response_text,
            "summary": f"{len(critical)} critical, {len(high)} high-risk, {len(warning)} warnings",
            "equipment_covered": [e["id"] for e in critical + high + warning],
        }

    async def _equipment_health_report(self, equipment_id: str) -> dict:
        """Generate detailed health report for a specific equipment."""
        eq = next((e for e in self.equipment_data if e["id"] == equipment_id), None)
        if not eq:
            return {"error": f"Equipment {equipment_id} not found"}

        history = [l for l in self.maintenance_logs if l["equipment_id"] == equipment_id][:10]
        failures = [f for f in self.failure_reports if f["equipment_id"] == equipment_id][:5]

        prompt = f"""Generate a detailed equipment health card report:

EQUIPMENT: {eq.get('name', '')}
ID: {eq.get('id', '')} | Type: {eq.get('type', '')} | Area: {eq.get('area', '')}
Criticality: {eq.get('criticality', '')} | Status: {eq.get('status', '')}
Health Score: {eq.get('health_score', 'N/A')}/100

RECENT MAINTENANCE ({len(history)} records):
{chr(10).join([f'- [{l["date"]}] {l["action_type"]}: {l["failure_mode"]} ({l["downtime_hours"]}h downtime)' for l in history[:5]])}

FAILURE HISTORY ({len(failures)} incidents):
{chr(10).join([f'- [{f["date"]}] {f["severity"]}: {f["failure_mode"]} — {f["root_cause"]}' for f in failures[:3]])}

Generate a comprehensive health report including:
1. **Equipment Health Summary**
2. **Maintenance History Analysis**
3. **Failure Pattern Analysis**
4. **Recommended Maintenance Strategy**
5. **Risk Assessment and Outlook**"""

        response_text = llm_client.generate_content("flash", prompt)

        return {
            "id": f"EHR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"Equipment Health Report — {eq.get('name', equipment_id)}",
            "type": "equipment_health",
            "generated_at": datetime.now().isoformat(),
            "content": response_text,
            "summary": f"Health: {eq.get('health_score', 'N/A')}/100, Status: {eq.get('status', 'N/A')}",
            "equipment_covered": [equipment_id],
        }

    async def _failure_analysis_report(self, equipment_id: str = None, area: str = None) -> dict:
        """Generate failure analysis report."""
        reports = self.failure_reports
        if equipment_id:
            reports = [r for r in reports if r["equipment_id"] == equipment_id]
        if area:
            reports = [r for r in reports if r["area"] == area]

        reports = reports[:20]

        prompt = f"""Analyze these failure reports and generate a failure analysis report:

FAILURE REPORTS ({len(reports)} total):
{chr(10).join([f'- [{r["date"]}] {r["equipment_name"]}: {r["failure_mode"]} (Severity: {r["severity"]}, Downtime: {r["downtime_hours"]}h, Loss: {r["production_loss_tonnes"]}T)' for r in reports[:10]])}

Generate:
1. **Failure Statistics Summary**
2. **Top Failure Modes** — most common failure types
3. **Root Cause Analysis** — systemic issues identified
4. **Impact Assessment** — total downtime and production losses
5. **Prevention Recommendations** — how to reduce failures
6. **Reliability Improvement Plan**"""

        response_text = llm_client.generate_content("flash", prompt)

        return {
            "id": f"FAR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"Failure Analysis Report",
            "type": "failure_analysis",
            "generated_at": datetime.now().isoformat(),
            "content": response_text,
            "summary": f"Analyzed {len(reports)} failure incidents",
            "equipment_covered": list(set(r["equipment_id"] for r in reports)),
        }


# Singleton
report_agent = ReportAgent()
