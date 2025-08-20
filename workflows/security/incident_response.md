# Incident Response Workflow (Draft)

1. Detection: Alert triggers (Prometheus/Alertmanager).
2. Triage: Severity, scope, initial containment.
3. Containment: Revoke credentials, block IPs/ranges, scale down affected components.
4. Eradication: Patch, rotate keys, cleanse data where required.
5. Recovery: Restore services, monitor closely.
6. Postmortem: Root cause analysis, action items, timelines.

Artifacts to attach: logs, timelines, evidence, communication notes.
