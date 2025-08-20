const assert = require('assert');
const fetch = require('node-fetch');

const BASE = process.env.N8N_BASE_URL || 'http://localhost:5678';
const PRESIGNED = process.env.S3_PRESIGNED_URL;

describe('Creative Agent — S3 Upload (presigned)', function () {
  this.timeout(20000);

  if (!PRESIGNED) {
    it('skipped: S3_PRESIGNED_URL not set', function () {
      this.skip();
    });
    return;
  }

  it('should generate content and upload to S3 via presigned URL', async () => {
    const res = await fetch(`${BASE}/webhook/creative/compose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        brief: 'Generate a short product tagline for a secure file storage app.',
        kind: 'text',
        style: { tone: 'concise, trustworthy' },
        iterations: 1,
        qualityThreshold: 0.4,
        s3: {
          preSignedUrl: PRESIGNED,
          bucket: 'test-bucket',
          key: 'creative/test-output.json'
        }
      }),
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.ok(body.status);
    assert.ok(body.output);
  });
});
