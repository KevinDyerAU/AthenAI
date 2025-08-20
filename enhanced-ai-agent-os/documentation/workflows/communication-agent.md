# Communication Agent Workflow

- __Purpose__: Multi-channel messaging, routing, delivery, engagement tracking, and compliance.
- __Entry__: `POST /webhook/communication/run`
- __Tools__: Email Delivery, Social Media

## Nodes
- __Webhook Communication Input__: receives `{ message, audience?, channels?, schedule?, metadata?, compliance? }`.
- __Normalize Input__: validates and shapes inputs.
- __Message Routing__: computes channel order from preferences.
- __Email Delivery__: `/webhook/communication/tools/email-delivery` builds email payload.
- __Social Media__: `/webhook/communication/tools/social-media` builds social posts.
- __AI Synthesize Comm Plan__: composes structured execution plan with analytics and follow-ups.
- __Respond__: returns `{ status, plan, email, social, routing }`.

## Example Request
```json
{
  "message": "Upcoming feature launch this Friday. Join our webinar!",
  "audience": {"segments": ["customers", "prospects"]},
  "channels": ["email", "social"],
  "metadata": {"subject": "Launch Webinar", "tags": ["product", "webinar"]},
  "schedule": {"when": "2025-09-01T10:00:00Z"},
  "compliance": {"consent": true, "unsubscribe": true}
}
```

## Compliance Notes
- Honor consent/unsubscribe flags and log audit trails.
- Follow CAN-SPAM, GDPR, and platform policies.

## Outputs
- __plan__: structured JSON with `composed_messages, personalization_rules, schedule, ab_tests, compliance, delivery_plan, analytics, response_handling, risks, next_steps`.
