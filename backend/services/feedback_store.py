"""
Feedback Store — Stores and manages engineer feedback on AI recommendations.
Implements the feedback loop for continuous improvement.
"""
import json
import os
from datetime import datetime
from backend.config import settings


FEEDBACK_FILE = os.path.join(settings.DATA_DIR, "feedback.json")


class FeedbackStore:
    """Manages feedback from maintenance engineers on AI recommendations."""

    def __init__(self):
        self.feedback_data = []
        self._load()

    def _load(self):
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, "r") as f:
                self.feedback_data = json.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
        with open(FEEDBACK_FILE, "w") as f:
            json.dump(self.feedback_data, f, indent=2)

    def add_feedback(self, session_id: str, message_index: int,
                     feedback_type: str, comment: str = None, correction: str = None):
        """Add feedback entry."""
        entry = {
            "id": f"FB-{len(self.feedback_data)+1:04d}",
            "session_id": session_id,
            "message_index": message_index,
            "feedback_type": feedback_type,
            "comment": comment,
            "correction": correction,
            "timestamp": datetime.now().isoformat(),
        }
        self.feedback_data.append(entry)
        self._save()
        return entry

    def get_stats(self) -> dict:
        """Get feedback statistics."""
        total = len(self.feedback_data)
        positive = sum(1 for f in self.feedback_data if f["feedback_type"] == "thumbs_up")
        negative = sum(1 for f in self.feedback_data if f["feedback_type"] == "thumbs_down")
        rate = positive / total if total > 0 else 0

        return {
            "total_feedback": total,
            "positive": positive,
            "negative": negative,
            "improvement_rate": round(rate, 2),
            "recent_feedback": self.feedback_data[-10:]
        }

    def get_corrections(self) -> list:
        """Get all corrections for learning."""
        return [f for f in self.feedback_data if f.get("correction")]


# Singleton
feedback_store = FeedbackStore()
