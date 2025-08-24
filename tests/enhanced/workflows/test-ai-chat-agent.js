// AI Chat Agent workflow integration tests
// Requires n8n running with `ai-chat-agent.json` and `master-orchestration-agent.json` imported and activated
// Node.js >= 18

import test from 'node:test';
import assert from 'node:assert/strict';

const BASE_URL = process.env.N8N_BASE_URL || 'http://localhost:5678';
const CHAT_SEND = `${BASE_URL}/webhook/chat/send`;
const CHAT_HISTORY = `${BASE_URL}/webhook/chat/history`;

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res;
}

const sessionId = 'test-session-chat-1';

test('Chat send returns ok or delegated with reply', async (t) => {
  const res = await postJSON(CHAT_SEND, {
    message: 'Hello there! Can you say hi back?',
    sessionId,
    userId: 'user-1'
  });

  if (res.status === 404 || res.status === 503) {
    t.skip(`Endpoint not available (${res.status}). Ensure workflows are imported + activated.`);
    return;
  }

  assert.equal(res.status, 200);
  const data = await res.json();
  assert.ok(['ok','delegated'].includes(data.status));
  assert.ok(typeof data.reply === 'string');
});

test('Chat history returns messages', async (t) => {
  const res = await postJSON(CHAT_HISTORY, { sessionId, limit: 10 });

  if (res.status === 404 || res.status === 503) {
    t.skip(`Endpoint not available (${res.status}). Ensure workflows are imported + activated.`);
    return;
  }

  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(data.sessionId, sessionId);
  assert.ok(Array.isArray(data.history));
});
