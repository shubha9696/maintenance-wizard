"""
Diagnostic Agent — Diagnoses equipment issues using symptoms,
sensor data, and historical failure patterns via chain-of-thought reasoning.
"""
import json
import os
from backend.config import settings
from backend.agents.knowledge_agent import knowledge_agent
from backend.services.llm_client import llm_client


class DiagnosticAgent:
    """Performs equipment fault diagnosis and root cause analysis."""

    def __init__(self):
        self.failure_modes = {}
        self._load_failure_modes()

    def _load_failure_modes(self):
        path = os.path.join(settings.DATA_DIR, "failure_modes.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.failure_modes = json.load(f)

    async def diagnose(self, query: str, equipment_id: str = None,
                       equipment_type: str = None, sensor_data: dict = None) -> dict:
        """
        Perform comprehensive equipment diagnosis using multi-step reasoning.
        """
        # Step 1: Retrieve relevant knowledge
        kb_results = await knowledge_agent.search_and_synthesize(
            query, equipment_id=equipment_id, equipment_type=equipment_type
        )

        # Step 2: Get known failure modes for equipment type
        known_modes = self.failure_modes.get(equipment_type, [])
        failure_modes_text = ""
        if known_modes:
            failure_modes_text = "KNOWN FAILURE MODES FOR THIS EQUIPMENT TYPE:\n"
            for fm in known_modes:
                failure_modes_text += f"- {fm['mode']}: Cause={fm['cause']}, Symptom={fm['symptom']}, MTBF={fm.get('mtbf_hours', 'N/A')}hrs\n"

        # Step 3: Get similar historical failures
        similar_failures = await knowledge_agent.get_similar_failures(query, equipment_id)
        history_text = ""
        if similar_failures:
            history_text = "SIMILAR HISTORICAL FAILURES:\n"
            for sf in similar_failures[:3]:
                history_text += f"- {sf['content'][:300]}...\n\n"

        # Step 4: Sensor data context
        sensor_context = ""
        if sensor_data:
            recent = sensor_data[-6:] if isinstance(sensor_data, list) else []
            if recent:
                sensor_context = "RECENT SENSOR READINGS:\n"
                for r in recent:
                    sensor_context += f"  [{r.get('timestamp', 'N/A')}] Vibration: {r.get('vibration', 'N/A')} mm/s, Temp: {r.get('temperature', 'N/A')}°C, Pressure: {r.get('pressure', 'N/A')} bar, Current: {r.get('current', 'N/A')} A\n"

        # Step 5: Chain-of-thought diagnosis with Gemini
        prompt = f"""You are an expert industrial maintenance diagnostic system for a steel manufacturing plant.
Perform a thorough diagnosis using chain-of-thought reasoning.

EQUIPMENT: {equipment_type or 'Unknown'} (ID: {equipment_id or 'Not specified'})

USER REPORTED ISSUE: {query}

{sensor_context}

{failure_modes_text}

{history_text}

KNOWLEDGE BASE FINDINGS:
{kb_results.get('answer', 'No additional context available.')}

INSTRUCTIONS - Provide a structured diagnosis:

1. **SYMPTOM ANALYSIS**: What symptoms are described or evident from sensor data?
2. **PROBABLE DIAGNOSES**: List top 3 most likely diagnoses ranked by probability (percentage).
3. **ROOT CAUSE ANALYSIS**: For the most likely diagnosis, explain the chain of causation.
4. **EVIDENCE**: What evidence supports each diagnosis?
5. **RISK ASSESSMENT**: What is the risk if unaddressed? (Low/Medium/High/Critical)
6. **IMMEDIATE ACTIONS**: What should be done right now?
7. **FURTHER INVESTIGATION**: What additional checks would confirm the diagnosis?

Format your response in clear sections with markdown formatting. Be specific and technical."""

        response_text = llm_client.generate_content("pro", prompt)

        # Determine risk level from response
        response_lower = response_text.lower()
        if "critical" in response_lower and ("risk" in response_lower or "immediate" in response_lower):
            risk = "critical"
        elif "high" in response_lower and "risk" in response_lower:
            risk = "high"
        elif "medium" in response_lower:
            risk = "medium"
        else:
            risk = "low"

        return {
            "diagnosis": response_text,
            "risk_level": risk,
            "equipment_id": equipment_id,
            "equipment_type": equipment_type,
            "sources": kb_results.get("sources", []),
            "similar_failures_found": len(similar_failures),
            "known_failure_modes": len(known_modes),
            "agent": "diagnostic"
        }


# Singleton
diagnostic_agent = DiagnosticAgent()
