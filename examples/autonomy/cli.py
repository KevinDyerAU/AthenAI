import argparse
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

# Ensure project root is on sys.path when running examples directly
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from examples.autonomy.simple_agent import build_agent


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal orchestrator for ExampleAgent")
    parser.add_argument("--agent-id", default="example-agent", help="Agent identifier")
    parser.add_argument("--run-seconds", type=int, default=60, help="How long to run before exiting")
    parser.add_argument("--task-interval", type=int, default=5, help="Seconds between simulated tasks")
    args = parser.parse_args()

    agent = build_agent(agent_id=args.agent_id)
    agent.start()

    start = time.time()
    next_task = 0.0
    try:
        while time.time() - start < args.run_seconds:
            now = time.time()
            if now - next_task >= args.task_interval:
                # simulate a simple task
                agent.process_task({"type": "demo", "at": datetime.now(timezone.utc).isoformat()})
                next_task = now
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        agent.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
