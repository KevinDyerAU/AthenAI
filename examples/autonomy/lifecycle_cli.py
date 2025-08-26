import argparse
import json
import os
from typing import List, Set

from api.services.autonomy.agent_lifecycle_manager import AgentLifecycleManager, AgentNeed
from api.services.autonomy.autonomous_agent_base import AgentCapability


def parse_caps(caps: List[str]) -> Set[AgentCapability]:
    out: Set[AgentCapability] = set()
    for c in caps or []:
        try:
            out.add(AgentCapability(c))
        except Exception:
            pass
    return out


def main():
    parser = argparse.ArgumentParser(description="Trigger manual AgentLifecycleManager creation requests")
    parser.add_argument("need_type", help="AgentNeed enum value, e.g. capability_gap")
    parser.add_argument("--caps", nargs="*", default=[], help="AgentCapability values, e.g. analysis execution integration")
    parser.add_argument("--priority", type=int, default=7)
    parser.add_argument("--justification", default="manual")
    parser.add_argument("--perf", default="{}", help="JSON string for performance requirements")
    parser.add_argument("--integrations", nargs="*", default=[], help="Integration requirements")
    parser.add_argument("--sync", action="store_true", help="Run design/dev/test/deploy synchronously (for debugging)")

    args = parser.parse_args()

    try:
        need_enum = AgentNeed(args.need_type)
    except Exception:
        raise SystemExit(f"Invalid need_type: {args.need_type}")

    caps = parse_caps(args.caps)
    try:
        perf = json.loads(args.perf)
    except Exception:
        raise SystemExit("--perf must be a valid JSON string")

    mgr = AgentLifecycleManager()
    need = {
        "type": need_enum,
        "required_capabilities": caps,
        "priority": args.priority,
        "justification": args.justification,
        "performance_requirements": perf,
        "integration_requirements": args.integrations,
    }
    request_id = mgr._create_agent_request(need)
    print(json.dumps({"status": "queued", "request_id": request_id}))

    if args.sync:
        # Run end-to-end synchronously once
        mgr._process_creation_request(request_id)
        print(json.dumps({"status": "processed", "request_id": request_id, "deployed_agents": list(mgr._deployed_agents.keys())}))


if __name__ == "__main__":
    main()
