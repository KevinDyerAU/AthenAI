# Planning Agent Workflow

- __Purpose__: Strategic planning, resource allocation, timeline optimization, and risk assessment for multi-agent projects.
- __Entry__: `POST /webhook/planning/run`
- __Tools__: Resource Allocation, Timeline Optimization

## Nodes
- __Webhook Planning Input__: receives `{ goals, constraints?, agents?, tasks?, methodology?, horizon? }`.
- __Normalize Input__: validates and shapes inputs.
- __Resource Allocation__: `/webhook/planning/tools/resource-allocation` assigns tasks to agents by skills/capacity.
- __Timeline Optimization__: `/webhook/planning/tools/timeline-optimization` creates a dependency-aware schedule and critical path.
- __AI Synthesize Plan__: composes structured strategic plan.
- __Respond__: returns `{ status, plan, allocation, schedule }`.

## Example Request
```json
{
  "goals": ["Ship v1", "Meet SLA"],
  "constraints": {"work_week_hours": 40},
  "agents": [
    {"name": "Analysis", "skills": ["stats", "ml"], "capacity": {"units": 40}},
    {"name": "Development", "skills": ["js", "python"], "capacity": {"units": 40}}
  ],
  "tasks": [
    {"id": "T1", "title": "Design", "effort": 16, "skills": ["js"], "deps": []},
    {"id": "T2", "title": "Implement", "effort": 32, "skills": ["js"], "deps": ["T1"]},
    {"id": "T3", "title": "Test", "effort": 16, "skills": ["python"], "deps": ["T2"]}
  ],
  "methodology": "hybrid",
  "horizon": {"start": "2025-09-01T00:00:00Z"}
}
```

## Outputs
- __plan__: strict JSON containing `strategy, goal_breakdown, prioritized_backlog, allocation_summary, schedule, risks, mitigations, monitoring, metrics, methodology, scenario_analysis, replanning_triggers, next_steps`.
- __allocation__: `{ assignments, remainingCapacity }`.
- __schedule__: array of tasks with `start`, `end`, `duration_days`, and `critical` flag; includes `critical_path`.

## Notes
- Replace Function tool nodes with OR tools (solver/Monte Carlo) or external PM systems while preserving the webhook contracts.
- Configure AI provider credentials in n8n for the AI Agent node.
