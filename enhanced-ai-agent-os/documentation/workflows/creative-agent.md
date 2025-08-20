# Creative Agent

Purpose: multi-modal content generation and iterative refinement with brand/style adherence.

Endpoints
- POST `/webhook/creative/compose` — main orchestration
- POST `/webhook/creative/tools/content-generate` — multi-modal generation (text, image, audio)
- POST `/webhook/creative/tools/style-management` — style evaluation and profile handling
 - POST `/webhook/creative/tools/storage-s3` — presigned S3 upload helper

Prereqs
- Configure OpenAI credential in n8n (text, image, TTS)
- Optional: set `MIDJOURNEY_WEBHOOK_URL` for Midjourney relay
 - For S3 uploads: client must provide a valid `preSignedUrl` (or add a server-side signer workflow)
 - For Style Profiles CRUD: configure Postgres credential named `postgres` and run `infrastructure/database/create_brand_profiles.sql`

Workflow Overview
- `workflows/creative-agent.json`
  - Normalize brief, style, kind, iterations, threshold
  - Pre-evaluate brief with `style-management`
  - Generate initial output with `content-generation`
  - Evaluate output style and quality
  - If below threshold, revise with AI and loop
  - If `s3.preSignedUrl` provided, upload final output to S3
  - Respond with final output, evaluation, iterations
- Tools
  - `creative-tools/content-generation.json`: routes by kind to GPT-4 (text), OpenAI Images or Midjourney (image), OpenAI TTS (audio)
  - `creative-tools/style-management.json`: AI-based adherence scoring and brand profile CRUD (Postgres)
  - `creative-tools/storage-s3.json`: HTTP PUT helper to presigned S3 URLs

Request Examples
```json
POST /webhook/creative/compose
{
  "brief": "Write a 150-word launch announcement for our AI feature.",
  "kind": "text",
  "style": {"tone":"confident, friendly","forbidden_terms":["cheap"]},
  "iterations": 2,
  "qualityThreshold": 0.8,
  "s3": {
    "preSignedUrl": "https://s3.amazonaws.com/bucket/key?...signature...",
    "bucket": "bucket",
    "key": "creative/outputs/announcement.json"
  }
}
```

Responses
- `status`, `output`, `evaluation`, `iterations`

Notes
- Extend video scripting via text mode; connect external render pipelines later.
- For asset mgmt/versioning, you can provide a presigned URL to store the final output to S3.
- Add human-in-the-loop by posting drafts to Slack/Jira and capturing feedback to `feedback` field.

## Style Profiles CRUD

Endpoint: `POST /webhook/creative/tools/style-management`

- Create
```json
{"action":"profile_create","profile":{"name":"Acme","guidelines":{"tone":"confident"}}}
```

- Get
```json
{"action":"profile_get","name":"Acme"}
```

- Update
```json
{"action":"profile_update","profile":{"name":"Acme","guidelines":{"tone":"confident","claims":"no unverifiable claims"}}}
```

- List
```json
{"action":"profile_list","limit":20,"offset":0}
```

- Delete
```json
{"action":"profile_delete","name":"Acme"}
```

Prerequisite: Postgres credential `postgres` and run `infrastructure/database/create_brand_profiles.sql`.

## S3 Upload Helper

Endpoint: `POST /webhook/creative/tools/storage-s3`

Body:
```json
{
  "content": {"kind":"text","output":"..."},
  "contentType": "application/json",
  "preSignedUrl": "https://s3.amazonaws.com/bucket/key?...",
  "bucket": "bucket",
  "key": "key"
}
```

Note: This workflow expects a presigned URL provided by the client or another service.
