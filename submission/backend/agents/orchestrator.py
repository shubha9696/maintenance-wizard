"""
Orchestrator Agent — The brain of the Maintenance Wizard.
Routes user queries to specialized agents, manages conversation context,
and chains agents for complex multi-step reasoning.
"""
import json
import os
import uuid
from datetime import datetime
import google.generativeai as genai
from backend.config import settings
from backend.agents.diagnostic_agent import diagnostic_agent
from backend.agents.prediction_agent import prediction_agent
from backend.agents.recommendation_agent import recommendation_agent
from backend.agents.report_agent import report_agent
from backend.agents.knowledge_agent import knowledge_agent

from backend.services.llm_client import llm_client


class Orchestrator:
    """
    Central orchestrator that understands user intent and routes to
    the appropriate agent(s). Supports multi-turn conversation and
    agent chaining for complex queries.
    """

    def __init__(self):
        self.sessions = {}  # In-memory session store
        self.equipment_data = []
        self._load_equipment()

    def _load_equipment(self):
        eq_path = os.path.join(settings.DATA_DIR, "equipment.json")
        if os.path.exists(eq_path):
            with open(eq_path, "r") as f:
                self.equipment_data = json.load(f)

    def _find_equipment(self, query: str) -> dict:
        """Try to identify equipment mentioned in the query."""
        query_lower = query.lower()
        for eq in self.equipment_data:
            if eq["id"].lower() in query_lower:
                return eq
            name_parts = eq["name"].lower().split()
            if all(part in query_lower for part in name_parts if len(part) > 3):
                return eq
            # Check equipment type
            if eq["type"].lower() in query_lower:
                return eq
        return {}

    async def classify_intent(self, query: str, context: list = None) -> dict:
        """Classify user intent to route to appropriate agent(s)."""
        context_text = ""
        if context:
            context_text = "\nRECENT CONVERSATION:\n" + "\n".join([
                f"{'User' if m['role']=='user' else 'Assistant'}: {m['content'][:200]}"
                for m in context[-4:]
            ])

        prompt = f"""Classify the intent of this maintenance engineer's query. 
Return a JSON object with the following fields:
- "primary_agent": one of ["diagnostic", "prediction", "recommendation", "report", "knowledge", "general"]
- "secondary_agents": list of additional agents to chain (can be empty)
- "equipment_mentioned": equipment name/ID if mentioned, else null
- "query_type": one of ["troubleshoot", "predict", "recommend", "report", "info", "status", "compare", "general"]
- "urgency": one of ["critical", "high", "medium", "low"]
- "requires_sensor_data": boolean
- "requires_history": boolean

{context_text}

USER QUERY: {query}

Return ONLY the JSON object, no explanation."""

        response_text = llm_client.generate_content("flash", prompt)
        try:
            # Clean response - remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                text = text.rsplit("```", 1)[0]
            return json.loads(text.strip())
        except (json.JSONDecodeError, Exception):
            return {
                "primary_agent": "knowledge",
                "secondary_agents": [],
                "equipment_mentioned": None,
                "query_type": "general",
                "urgency": "medium",
                "requires_sensor_data": False,
                "requires_history": False
            }

    async def process_query(self, message: str, session_id: str = None) -> dict:
        """Process a user query through the agentic pipeline."""
        # Session management
        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "equipment_context": None
            }

        session = self.sessions[session_id]
        session["messages"].append({"role": "user", "content": message, "timestamp": datetime.now().isoformat()})

        # Step 1: Classify intent
        intent = await self.classify_intent(message, session["messages"])

        # Step 2: Identify equipment
        equipment = self._find_equipment(message)
        if equipment:
            session["equipment_context"] = equipment
        elif session.get("equipment_context"):
            equipment = session["equipment_context"]

        eq_id = equipment.get("id") if equipment else intent.get("equipment_mentioned")
        eq_type = equipment.get("type") if equipment else None

        # Step 3: Load sensor data if needed
        sensor_data = None
        if intent.get("requires_sensor_data") and eq_id:
            sensor_path = os.path.join(settings.DATA_DIR, "sensor_data.json")
            if os.path.exists(sensor_path):
                with open(sensor_path, "r") as f:
                    all_sensors = json.load(f)
                sensor_data = all_sensors.get(eq_id, [])

        # Step 4: Route to primary agent
        primary = intent.get("primary_agent", "knowledge")
        result = {}
        agent_used = primary

        try:
            if primary == "diagnostic":
                result = await diagnostic_agent.diagnose(
                    message, equipment_id=eq_id, equipment_type=eq_type, sensor_data=sensor_data
                )
                response_text = result.get("diagnosis", "")

            elif primary == "prediction":
                if eq_id:
                    result = await prediction_agent.predict_equipment(eq_id)
                    response_text = result.get("interpretation", "")
                else:
                    warnings = await prediction_agent.get_early_warnings()
                    if warnings:
                        response_text = "## Early Warnings & Predictions\n\n"
                        for w in warnings[:5]:
                            response_text += f"**{w['equipment_name']}** ({w['area']})\n"
                            response_text += f"- Risk: {w['risk_level'].upper()} | Health: {w['current_health']}/100\n"
                            response_text += f"- RUL: {w['rul_days']:.0f} days | Failure Prob (30d): {w['failure_probability_30d']*100:.0f}%\n"
                            response_text += f"- {w['warning']}\n\n"
                    else:
                        response_text = "All equipment is currently within normal operating parameters. No early warnings to report."
                    result = {"warnings": warnings}

            elif primary == "recommendation":
                result = await recommendation_agent.generate_recommendations(
                    message, equipment_id=eq_id
                )
                response_text = result.get("recommendations", "")

            elif primary == "report":
                query_lower = message.lower()
                report_type = "maintenance_summary"
                if "alert" in query_lower:
                    report_type = "alert_summary"
                elif "health" in query_lower:
                    report_type = "equipment_health"
                elif "failure" in query_lower or "analysis" in query_lower:
                    report_type = "failure_analysis"

                result = await report_agent.generate_report(
                    report_type=report_type, equipment_id=eq_id
                )
                response_text = result.get("content", "")

            elif primary == "knowledge":
                result = await knowledge_agent.search_and_synthesize(
                    message, equipment_id=eq_id, equipment_type=eq_type
                )
                response_text = result.get("answer", "")

            else:
                # General query — use knowledge agent with broader context
                result = await knowledge_agent.search_and_synthesize(
                    message, equipment_id=eq_id, equipment_type=eq_type
                )
                response_text = result.get("answer", "")

        except Exception as e:
            response_text = f"I encountered an issue while processing your query: {str(e)}. Please try rephrasing your question."
            result = {"error": str(e)}

        # Step 5: Chain secondary agents if needed
        secondary_results = {}
        for secondary in intent.get("secondary_agents", []):
            try:
                if secondary == "recommendation" and primary != "recommendation":
                    sec_result = await recommendation_agent.generate_recommendations(
                        message, diagnosis=result if primary == "diagnostic" else None,
                        prediction=result if primary == "prediction" else None,
                        equipment_id=eq_id
                    )
                    response_text += "\n\n---\n\n## Recommendations\n\n" + sec_result.get("recommendations", "")
                    secondary_results["recommendation"] = sec_result

                elif secondary == "prediction" and primary != "prediction" and eq_id:
                    sec_result = await prediction_agent.predict_equipment(eq_id)
                    response_text += f"\n\n---\n\n## Prediction\n\n{sec_result.get('interpretation', '')}"
                    secondary_results["prediction"] = sec_result

            except Exception:
                pass  # Don't fail on secondary agent errors

        # Step 6: Store response in session
        session["messages"].append({
            "role": "assistant",
            "content": response_text,
            "agent": agent_used,
            "timestamp": datetime.now().isoformat()
        })

        # Build response
        sources = result.get("sources", [])
        return {
            "response": response_text,
            "session_id": session_id,
            "agent_used": agent_used,
            "sources": sources,
            "risk_level": result.get("risk_level"),
            "equipment_id": eq_id,
            "recommendations": result.get("recommendation_list", []),
            "metadata": {
                "intent": intent,
                "equipment_detected": equipment.get("name") if equipment else None,
                "secondary_agents": list(secondary_results.keys()),
                "message_count": len(session["messages"])
            }
        }

    def get_session_history(self, session_id: str) -> list:
        """Get conversation history for a session."""
        session = self.sessions.get(session_id, {})
        return session.get("messages", [])


# Singleton
orchestrator = Orchestrator()
