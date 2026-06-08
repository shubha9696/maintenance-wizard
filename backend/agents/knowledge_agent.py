"""
Knowledge Retrieval Agent — RAG-powered agent for searching equipment
documentation, SOPs, maintenance records, and failure databases.
"""
import os
import json
from backend.config import settings
from backend.services.vector_store import vector_store
from backend.services.llm_client import llm_client


class KnowledgeAgent:
    """Retrieves and synthesizes information from the equipment knowledge base."""

    def __init__(self):
        pass

    async def search_and_synthesize(self, query: str, equipment_id: str = None,
                                     equipment_type: str = None) -> dict:
        """Search knowledge base and synthesize a coherent answer."""
        # Fetch equipment_type if not provided
        if equipment_id and not equipment_type:
            try:
                eq_path = os.path.join(settings.DATA_DIR, "equipment.json")
                if os.path.exists(eq_path):
                    with open(eq_path, "r", encoding="utf-8") as f:
                        eq_list = json.load(f)
                        for eq in eq_list:
                            if eq["id"] == equipment_id:
                                equipment_type = eq.get("type")
                                break
            except Exception:
                pass

        # Search across all collections
        results = vector_store.search_all(query, n_results=5, equipment_id=equipment_id)

        # Also search failure modes if equipment type is provided
        if equipment_type:
            fm_results = vector_store.search_failure_modes(query, n_results=3, equipment_type=equipment_type)
            results.extend(fm_results)

        # Dynamic injection of spare parts if query is about spare parts
        query_lower = query.lower()
        if any(term in query_lower for term in ["spare", "part", "inventory", "stock", "spares"]):
            spares_path = os.path.join(settings.DATA_DIR, "spare_parts.json")
            if os.path.exists(spares_path):
                try:
                    with open(spares_path, "r", encoding="utf-8") as f:
                        spares_data = json.load(f)
                    
                    spares_str = ""
                    if equipment_type and equipment_type in spares_data:
                        spares_list = spares_data[equipment_type]
                        spares_str = f"SPARE PARTS INVENTORY for {equipment_type} (applicable to {equipment_id or 'this equipment'}):\n"
                        for sp in spares_list:
                            availability = f"{sp['stock']} in stock" if sp['stock'] > 0 else f"OUT OF STOCK (Lead time: {sp['lead_time_days']} days)"
                            spares_str += f"- {sp['name']} (Part No: {sp['part_no']}): Cost ₹{sp['cost']:,} | Availability: {availability} | Current Qty: {sp['stock']}\n"
                    elif not equipment_type:
                        spares_str = "SPARE PARTS INVENTORY (All Equipment Types):\n"
                        for eq_t, spares_list in spares_data.items():
                            spares_str += f"\nEquipment Type: {eq_t}\n"
                            for sp in spares_list:
                                availability = f"{sp['stock']} in stock" if sp['stock'] > 0 else f"OUT OF STOCK (Lead time: {sp['lead_time_days']} days)"
                                spares_str += f"- {sp['name']} (Part No: {sp['part_no']}): Cost ₹{sp['cost']:,} | Availability: {availability} | Current Qty: {sp['stock']}\n"
                    
                    if spares_str:
                        results.insert(0, {
                            "content": spares_str,
                            "metadata": {
                                "doc_type": "spare_parts_inventory",
                                "source": "spare_parts.json"
                            },
                            "relevance_score": 1.0,
                            "distance": 0.0
                        })
                except Exception as e:
                    print(f"Error loading spare parts in KnowledgeAgent: {e}")

        if not results:
            return {
                "answer": "No relevant information found in the knowledge base for this query.",
                "sources": [],
                "confidence": 0.0
            }

        # Build context from retrieved documents
        context_parts = []
        sources = []
        for i, result in enumerate(results[:8]):
            context_parts.append(f"[Source {i+1}] ({result['metadata'].get('doc_type', 'unknown')}):\n{result['content']}")
            sources.append({
                "document": result["metadata"].get("source", result["metadata"].get("doc_type", "unknown")),
                "section": result["metadata"].get("doc_type", ""),
                "relevance_score": result.get("relevance_score", 0.5),
                "content": result["content"]
            })


        context = "\n\n---\n\n".join(context_parts)

        # Use Gemini to synthesize
        prompt = f"""You are a maintenance knowledge expert for a steel manufacturing plant. 
Based on the following retrieved documents, answer the user's question accurately and thoroughly.

RETRIEVED DOCUMENTS:
{context}

USER QUESTION: {query}

Instructions:
- Provide a detailed, technical answer based on the retrieved documents
- Reference specific sources when making claims (e.g., "According to the pump maintenance SOP...")
- If the documents contain specific procedures, list them step-by-step
- Include relevant safety warnings
- If information is insufficient, clearly state what is missing
- Use proper engineering terminology

Provide your answer:"""

        response_text = llm_client.generate_content("flash", prompt)

        avg_relevance = sum(r.get("relevance_score", 0.5) for r in sources) / len(sources) if sources else 0

        return {
            "answer": response_text,
            "sources": sources[:5],
            "confidence": round(avg_relevance, 2),
            "num_sources": len(sources)
        }

    async def get_equipment_manual(self, equipment_type: str) -> dict:
        """Retrieve manual information for a specific equipment type."""
        results = vector_store.search_knowledge(
            f"maintenance manual procedures for {equipment_type}",
            n_results=5,
            doc_type="manual"
        )
        sop_results = vector_store.search_knowledge(
            f"SOP standard operating procedure for {equipment_type}",
            n_results=5,
            doc_type="sop"
        )
        results.extend(sop_results)

        return {
            "equipment_type": equipment_type,
            "documents": [{"content": r["content"], "source": r["metadata"].get("source", "")} for r in results],
            "count": len(results)
        }

    async def get_similar_failures(self, failure_description: str, equipment_id: str = None) -> list:
        """Find similar historical failures."""
        results = vector_store.search_failure_reports(
            failure_description, n_results=5, equipment_id=equipment_id
        )
        return [
            {
                "content": r["content"],
                "relevance": r.get("relevance_score", 0.5),
                "metadata": r["metadata"]
            }
            for r in results
        ]


# Singleton
knowledge_agent = KnowledgeAgent()
