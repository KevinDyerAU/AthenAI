# Creative Tool — Content Generation

Purpose: multi-modal content generation routed by kind (text, image, audio).

- Workflow: `workflows/creative-tools/content-generation.json`
- Webhook: `POST /webhook/creative/tools/content-generate`

## Prerequisites
- OpenAI credential in n8n (GPT-4, Images, and TTS)
- Optional: `MIDJOURNEY_WEBHOOK_URL` for Midjourney relay

## Request
```json
{
  "kind": "text|image|audio",
  "prompt": "...",
  "style": {"tone":"..."},
  "model": "optional",
  "assets": {"references":[]}
}
```

## Response (shape)
- `kind`: echo of requested kind
- `output`: generated payload (text, image URL/base64, or audio URL/base64)

## Recommended Next Steps
- Add video generation routing
- Add safety filters/NSFW guardrails
- Add deterministic mode and seed control for images
- Add streaming support for long text
