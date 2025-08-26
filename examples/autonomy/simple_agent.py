import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any

# Ensure project root is on sys.path when running examples directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.services.autonomy.autonomous_agent_base import (
    AutonomousAgentBase,
    AgentPersonality,
    AgentCapability,
)


class ExampleAgent(AutonomousAgentBase):
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate doing a unit of work
        self.metrics.tasks_completed += 1
        self.metrics.average_response_time = 0.2
        self.metrics.last_activity = datetime.now(timezone.utc)
        return {"status": "done", "task": task}


def build_agent(agent_id: str = "example-agent") -> ExampleAgent:
    personality = AgentPersonality(
        name="Example",
        role="demo",
        capabilities={AgentCapability.RESEARCH, AgentCapability.ANALYSIS},
        personality_traits={"curiosity": 0.8},
        decision_making_style="analytical",
        communication_style="concise",
    )
    return ExampleAgent(agent_id=agent_id, personality=personality)
