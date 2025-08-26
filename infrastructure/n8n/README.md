# n8n Workflow Orchestration Templates

This folder contains ready-to-import n8n workflow templates that orchestrate agent lifecycle, health monitoring, knowledge drift remediation, self-healing, and human-in-the-loop operations for NeoV3.

## Files

- `config/n8n_agent_orchestration_workflows.json` — Export bundle with four workflows:
  - Agent Lifecycle Orchestration
  - Agent Health Monitoring
  - Knowledge Drift Orchestration
  - Self-Healing Orchestration
  - Human-in-the-Loop Approvals

## API endpoint mapping (NeoV3)

- Create lifecycle request: `POST /api/autonomy/lifecycle/requests`
- Lifecycle manager: 
  - Start: `POST /api/autonomy/lifecycle/manager/start`
  - Stop: `POST /api/autonomy/lifecycle/manager/stop`
  - Status: `GET /api/autonomy/lifecycle/manager/status`
- Retire agent: `POST /api/autonomy/lifecycle/retire`
- Metrics (examples):
  - Drift check: `GET /api/autonomy/metrics/drift/check`
  - Remediate drift: `POST /api/autonomy/metrics/drift/remediate`
  - Queue remediation: `POST /api/autonomy/metrics/drift/queue-remediation`

Adjust `api_base_url` by setting it in the inbound payload or by editing nodes to your deployment base URL.

## Import steps

1. Start n8n (Docker or local) and open the UI (default http://localhost:5678).
2. Import `config/n8n_agent_orchestration_workflows.json` via Import.
3. Configure any credentials (e.g., HTTP header auth, Slack webhook) as needed.
4. For each webhook workflow (paths: `agent-lifecycle`, `agent-healing`, `approval`), copy the production webhook URL from n8n and update any external triggers accordingly.

## Using the workflows

- Agent Lifecycle Orchestration
  - POST to the `agent-lifecycle` webhook with JSON:
    ```json
    {
      "action": "create_agent",
      "api_base_url": "http://localhost:8000",
      "need_type": "capability_gap",
      "required_capabilities": ["execution"],
      "priority": 8,
      "justification": "manual"
    }
    ```
  - Or start manager: `{ "action": "start_manager", "api_base_url": "http://localhost:8000" }`

- Agent Health Monitoring
  - Runs every 5 minutes:
    - Calls `GET /api/autonomy/lifecycle/manager/status`
    - Splits `deployed_agents`
    - Notifies Slack if `health_score < 0.6`
    - Retires if `health_score < 0.3` via `POST /api/autonomy/lifecycle/retire`

- Knowledge Drift Orchestration
  - Runs every 15 minutes, calls drift check, then either remediate immediately or queue remediation, depending on severity.

- Self-Healing Orchestration
  - Webhook-triggered (`agent-healing`) with strategy routing. If `strategy == 'retire'`, calls retire API; otherwise you can extend to restart/scale.

- Human-in-the-Loop Approvals
  - Webhook (`approval`) that can start manager on approval.

## Customization

- Slack notifications: configure `slack_webhook_url` where needed.
- Health thresholds: adjust in IF nodes (0.6 warn, 0.3 critical by default).
- Schedules: change minute intervals in Schedule Trigger nodes.

## Testing

1. Ensure API is running locally (defaults host 0.0.0.0:8000).
2. In n8n, execute the `Agent Lifecycle Orchestration` webhook and observe a 202 response from the API and events published.
3. Use `GET /api/autonomy/lifecycle/manager/status` to verify agents.
4. Trigger `Self-Healing Orchestration` with `{ "strategy": "retire", "agent_id": "<id>", "api_base_url": "http://localhost:8000" }`.

## Troubleshooting

- If manager status shows `running: false`, start via `POST /api/autonomy/lifecycle/manager/start`.
- If Slack notifications fail, verify webhook URL and network egress.
- For webhook URLs, ensure your n8n instance is reachable from the caller (use the production webhook URL, not localhost, in distributed setups).
