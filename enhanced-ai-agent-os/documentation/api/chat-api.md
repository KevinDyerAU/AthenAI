# Chat API

This document describes REST endpoints and WebSocket bridge for the AI Chat Agent.

Workflow files:
- `workflows/ai-chat-agent.json`
- `workflows/chat-websocket-handler.json`

## REST Endpoints

- POST `/webhook/chat/send`
  - Request body:
    ```json
    {
      "message": "Summarize the latest Neo4j release notes",
      "sessionId": "s-abc",
      "userId": "u-123",
      "meta": {"source": "web"}
    }
    ```
  - Response examples:
    - Direct reply:
      ```json
      {"status":"ok","reply":"Here is a short summary ...","delegated":false}
      ```
    - Delegated to Master Orchestration Agent:
      ```json
      {"status":"delegated","reply":"Task delegated to Master Orchestration Agent.","orchestration":{"status":"accepted", "queue":"agents.research", "plan":["..."]}}
      ```

- POST `/webhook/chat/history`
  - Request body:
    ```json
    { "sessionId": "s-abc", "limit": 50 }
    ```
  - Response:
    ```json
    { "sessionId":"s-abc", "history":[{"role":"user","content":"...","created_at":"..."}]} 
    ```

## WebSocket Bridge (HTTP)

WebSocket events are proxied via HTTP webhook endpoints to keep compatibility with n8n nodes:
- Connect: POST `/webhook/ws/connect` → `{ sessionId, userId? }`
- Message: POST `/webhook/ws/message` → `{ sessionId, text }`
- Disconnect: POST `/webhook/ws/disconnect` → `{ sessionId }`

Use these three endpoints from your WS gateway (e.g., a thin Node.js/Edge adapter) to persist sessions and messages.

## Persistence

- Postgres schemas:
  - `infrastructure/database/sql/chat_schema.sql` for `chat_sessions` and `chat_messages`.
  - `infrastructure/database/sql/memory_schema.sql` for conversation memory used by the Master Orchestrator.

## Delegation Logic

- The Chat Agent uses `AI Chat (Chat Agent)` reasoning to decide whether to respond directly or delegate.
- If delegation is chosen, it invokes `POST /webhook/master/orchestrate` with user/context payload.

## Multi-model Support

- Configure credentials in the `AI Chat (Chat Agent)` node to switch providers:
  - OpenAI GPT-4 / GPT-4o
  - Anthropic Claude
  - Google Gemini

## Streaming Responses

- Basic immediate acknowledgments are supported.
- For streaming, attach an SSE/WS gateway that forwards partial tokens to the client while `AI Chat` processes. The current workflow returns final responses; streaming can be added by interposing a custom streaming node or external gateway.

## Error Handling

- Input validation errors return 4xx with descriptive messages from Function nodes.
- Downstream errors (Master/DB) are surfaced with user-friendly summaries; logs contain details.
