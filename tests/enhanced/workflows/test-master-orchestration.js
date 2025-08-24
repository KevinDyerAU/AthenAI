// Master Orchestration Agent workflow integration test
// Requires n8n running with `master-orchestration-agent.json` imported and activated
// Node.js >= 18 (built-in fetch)

import test from 'node:test';
import assert from 'node:assert/strict';

const BASE_URL = process.env.N8N_BASE_URL || 'http://localhost:5678';
const ENDPOINT = `${BASE_URL}/webhook/master/orchestrate`;

const samplePayload = {
  request: 'Summarize the latest Neo4j release notes',
  priority: 'high',
  context: { userId: 'u-123', sessionId: 's-abc' }
};

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res;
}

// Smoke test: endpoint responds and returns expected shape when active
// If the workflow isn't active, the test is skipped with a helpful message.
test('Master Orchestration Agent endpoint responds with orchestration plan', async (t) => {
  const res = await postJSON(ENDPOINT, samplePayload);

  if (res.status === 404 || res.status === 503) {
    t.skip(`Endpoint not available (${res.status}). Ensure n8n is running and the workflow is imported + activated at ${ENDPOINT}`);
    return;
  }

  assert.equal(res.status, 200, `Expected 200 OK, got ${res.status}`);
  const data = await res.json();

  // Basic shape assertions (the workflow returns these keys)
  assert.equal(typeof data, 'object');
  assert.ok(data.status, 'missing status');
  assert.ok(Array.isArray(data.plan), 'plan should be array');
  assert.ok(data.queue, 'missing queue');
  assert.ok('primary_agent' in data, 'missing primary_agent');

  // Provide visibility for CI logs
  console.log('Response keys:', Object.keys(data));
});
