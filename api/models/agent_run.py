from datetime import datetime
from ..extensions import db


class AgentRun(db.Model):
    __tablename__ = "agent_runs"

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey("agents.id"), index=True, nullable=False)
    execution_id = db.Column(db.String(64), unique=True, index=True, nullable=False)

    status = db.Column(db.String(32), index=True, nullable=False, default="queued")
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)

    result = db.Column(db.JSON, nullable=True)
    error = db.Column(db.Text, nullable=True)
    metrics = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def compute_duration(self):
        if self.started_at and self.finished_at:
            self.duration_ms = int((self.finished_at - self.started_at).total_seconds() * 1000)
        return self.duration_ms
