"""
Recommendation Agent — Generates actionable maintenance recommendations
considering priority, spare parts, scheduling, and operational constraints.
"""
import json
import os
from backend.config import settings
from backend.services.vector_store import vector_store
from backend.services.llm_client import llm_client


class RecommendationAgent:
    """Generates prioritized maintenance recommendations."""

    def __init__(self):
        self.spare_parts = {}
        self.equipment_data = []
        self._load_data()

    def _load_data(self):
        spares_path = os.path.join(settings.DATA_DIR, "spare_parts.json")
        eq_path = os.path.join(settings.DATA_DIR, "equipment.json")

        if os.path.exists(spares_path):
            with open(spares_path, "r") as f:
                self.spare_parts = json.load(f)
        if os.path.exists(eq_path):
            with open(eq_path, "r") as f:
                self.equipment_data = json.load(f)

    async def generate_recommendations(self, query: str, diagnosis: dict = None,
                                         prediction: dict = None, equipment_id: str = None) -> dict:
        """Generate comprehensive maintenance recommendations."""
        if not self.spare_parts or not self.equipment_data:
            self._load_data()
        eq = next((e for e in self.equipment_data if e["id"] == equipment_id), {}) if equipment_id else {}
        eq_type = eq.get("type", "")

        # Get relevant SOPs
        sop_results = vector_store.search_knowledge(
            f"maintenance procedure repair {eq_type} {query}", n_results=3, doc_type="sop"
        )
        sop_context = "\n".join([r["content"] for r in sop_results]) if sop_results else "No specific SOP found."

        # Get spare parts info
        spares = self.spare_parts.get(eq_type, [])
        spares_text = ""
        if spares:
            spares_text = "AVAILABLE SPARE PARTS:\n"
            for sp in spares:
                availability = "IN STOCK" if sp["stock"] > 0 else f"LEAD TIME: {sp['lead_time_days']} days"
                spares_text += f"- {sp['name']} ({sp['part_no']}): Cost ₹{sp['cost']:,} | {availability} (Qty: {sp['stock']})\n"

        # Build diagnosis/prediction context
        diag_context = ""
        if diagnosis:
            diag_context = f"\nDIAGNOSIS:\n{diagnosis.get('diagnosis', 'N/A')[:500]}\nRisk: {diagnosis.get('risk_level', 'N/A')}"

        pred_context = ""
        if prediction:
            rul = prediction.get("rul", {})
            pred_context = (f"\nPREDICTION:\n"
                          f"- RUL: {rul.get('rul_days', 'N/A')} days\n"
                          f"- Health: {rul.get('current_health', 'N/A')}/100\n"
                          f"- Risk: {rul.get('risk_level', 'N/A')}\n"
                          f"- Trend: {rul.get('health_trend', 'N/A')}")

        prompt = f"""You are a senior maintenance planning engineer at a Tata Steel plant.
Generate detailed, actionable maintenance recommendations.

EQUIPMENT: {eq.get('name', 'Not specified')} ({eq_type})
Area: {eq.get('area', '')} | Criticality: {eq.get('criticality', '')}

USER REQUEST: {query}
{diag_context}
{pred_context}

RELEVANT SOPs AND PROCEDURES:
{sop_context}

{spares_text}

Generate a comprehensive recommendation covering:

## Immediate Actions (within 24 hours)
- List specific steps to take immediately
- Include safety precautions

## Short-term Maintenance Plan (1-7 days)
- Scheduled maintenance activities
- Required resources and personnel
- Parts to procure if not in stock

## Long-term Strategy (1-3 months)
- Preventive measures to avoid recurrence
- Monitoring plan with specific parameters and thresholds
- Suggested modifications or upgrades

## Spare Parts & Procurement
- Parts needed with availability status
- Emergency procurement recommendations if needed
- Cost estimate

## Priority Assessment
- Overall urgency: [Critical/High/Medium/Low]
- Justification for priority level
- Consequences of delayed action

## Estimated Downtime
- Time required for maintenance activities
- Best scheduling window to minimize production impact

Be specific with part numbers, procedures, and timeframes. Reference SOPs where applicable."""

        response_text = llm_client.generate_content("pro", prompt)

        # Extract recommendations as list
        recs = []
        for line in response_text.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                recs.append(line[2:].strip())

        return {
            "recommendations": response_text,
            "recommendation_list": recs[:15],
            "equipment_id": equipment_id,
            "spare_parts_info": spares,
            "sources": [{"document": r["metadata"].get("source", "SOP"), "section": "Maintenance Procedure", "relevance_score": r.get("relevance_score", 0.5), "content": r["content"]} for r in sop_results],
            "agent": "recommendation"
        }


    async def prioritize_maintenance(self, equipment_list: list = None) -> list:
        """Prioritize maintenance actions across all equipment."""
        if not self.equipment_data:
            self._load_data()
        if not equipment_list:
            equipment_list = self.equipment_data

        priorities = []
        for eq in equipment_list:
            risk = eq.get("risk_level", "low")
            health = eq.get("health_score", 80)
            criticality = eq.get("criticality", "medium")

            # Score: higher = more urgent
            risk_scores = {"critical": 40, "high": 30, "medium": 15, "low": 5}
            crit_scores = {"critical": 30, "high": 20, "medium": 10, "low": 5}
            health_penalty = max(0, (70 - health)) * 0.5

            score = risk_scores.get(risk, 5) + crit_scores.get(criticality, 10) + health_penalty

            priorities.append({
                "equipment_id": eq["id"],
                "equipment_name": eq.get("name", ""),
                "area": eq.get("area", ""),
                "priority_score": round(score, 1),
                "risk_level": risk,
                "health_score": health,
                "criticality": criticality,
                "recommended_action": self._quick_recommendation(risk, health, criticality)
            })

        priorities.sort(key=lambda p: -p["priority_score"])
        return priorities

    def _quick_recommendation(self, risk: str, health: float, criticality: str) -> str:
        if risk == "critical":
            return "IMMEDIATE: Schedule emergency maintenance within 24 hours"
        if risk == "high":
            return "URGENT: Plan corrective maintenance within 1 week"
        if health < 60:
            return "PLAN: Schedule condition-based maintenance within 2 weeks"
        if criticality == "critical" and health < 75:
            return "MONITOR: Increase inspection frequency, plan maintenance"
        return "ROUTINE: Continue normal preventive maintenance schedule"


# Singleton
recommendation_agent = RecommendationAgent()
