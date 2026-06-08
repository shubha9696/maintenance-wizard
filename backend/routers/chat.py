"""Chat router — Main conversational endpoint for the Maintenance Wizard."""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the agentic pipeline."""
    try:
        result = await orchestrator.process_query(
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    history = orchestrator.get_session_history(session_id)
    return {"session_id": session_id, "messages": history}
