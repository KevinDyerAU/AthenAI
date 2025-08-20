# Creative Tool — Style Management

Purpose: brand/style adherence evaluation and brand profile CRUD.

- Workflow: `workflows/creative-tools/style-management.json`
- Webhook: `POST /webhook/creative/tools/style-management`

## Prerequisites
- OpenAI credential in n8n
- Postgres credential named `postgres`
- Run `infrastructure/database/create_brand_profiles.sql`

## Actions
- `evaluate`: evaluates content against `guidelines`
- `profile_create`, `profile_update`, `profile_get`, `profile_delete`, `profile_list`

## Evaluate Example
```json
{"action":"evaluate","content":"...","guidelines":{"tone":"confident"}}
```

## CRUD Example
```json
{"action":"profile_create","profile":{"name":"Acme","guidelines":{"tone":"confident"}}}
```

## Response (shape)
- Evaluate: `{ status, result: { score, findings, violations, suggestions, risk_level } }`
- CRUD: `{ status, result }` (DB rows)

## Recommended Next Steps
- Add RBAC and audit logs for profile changes
- Add profile versioning and history
- Support hierarchical brand profiles (global > product > campaign)
- Add caching layer for hot profiles
