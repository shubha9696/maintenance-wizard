"""Feedback router — Engineer feedback on AI recommendations."""
from fastapi import APIRouter
from backend.models.schemas import FeedbackRequest
from backend.services.feedback_store import feedback_store

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback on an AI recommendation."""
    entry = feedback_store.add_feedback(
        session_id=request.session_id,
        message_index=request.message_index,
        feedback_type=request.feedback_type,
        comment=request.comment,
        correction=request.correction
    )
    return {"status": "recorded", "feedback": entry}


@router.get("/stats")
async def feedback_stats():
    """Get feedback statistics."""
    return feedback_store.get_stats()
