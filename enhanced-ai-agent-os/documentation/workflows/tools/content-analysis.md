# Research Tool — Content Analysis

Purpose: fetch URLs, extract text from HTML, and analyze with AI for summary, sentiment, entities, and insights.

- Workflow: `workflows/research-tools/content-analysis.json`
- Webhook: `POST /webhook/research/tools/content-analysis`

## Prerequisites
- OpenAI credential in n8n

## Request
```json
{"urls":["https://example.com/article"],"limit":5}
```

## Response (shape)
- For each URL: `{ url, analysis: { summary, key_insights, sentiment, entities, quality_notes } }`

## Recommended Next Steps
- Add boilerplate/remnant removal improvements (readability)
- Add language detection and translation option
- Add PII redaction for compliance
- Cache fetched pages to reduce re-analysis
