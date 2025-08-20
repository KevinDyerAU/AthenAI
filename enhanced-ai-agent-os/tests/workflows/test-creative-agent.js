const assert = require('assert');
const fetch = require('node-fetch');

const BASE = process.env.N8N_BASE_URL || 'http://localhost:5678';

describe('Creative Agent', function () {
  this.timeout(20000);

  it('should generate and refine text content', async () => {
    const res = await fetch(`${BASE}/webhook/creative/compose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        brief: 'Write a 50-word teaser for our cybersecurity webinar.',
        kind: 'text',
        style: { tone: 'professional, engaging' },
        iterations: 1,
        qualityThreshold: 0.5
      }),
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.ok(body.status);
    assert.ok(body.output);
  });
});
