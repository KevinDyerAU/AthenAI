# Research Tool — Academic Search (Semantic Scholar)

Purpose: academic paper search and normalization of results.

- Workflow: `workflows/research-tools/academic-search.json`
- Webhook: `POST /webhook/research/tools/academic-search`

## Prerequisites
- Semantic Scholar API key (if required by your usage tier), configured in n8n if used

## Request
```json
{"query":"graph neural networks","limit":5}
```

## Response (shape)
- `{ results: [ { title, url, authors, year, venue, abstract } ] }`

## Recommended Next Steps
- Add filters (years, venues, authors)
- Add pagination and cursoring
- Add paper detail fetch with citations/refs
- Add deduplication across sources
