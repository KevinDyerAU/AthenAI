const assert = require('assert');
const fetch = require('node-fetch');

const BASE = process.env.N8N_BASE_URL || 'http://localhost:5678';
const RUN = process.env.TEST_PROFILES === '1';

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch (e) { json = { raw: text }; }
  return { status: res.status, body: json };
}

describe('Style Profiles CRUD', function () {
  this.timeout(20000);

  if (!RUN) {
    it('skipped: set TEST_PROFILES=1 and ensure Postgres credential is configured in n8n', function () {
      this.skip();
    });
    return;
  }

  const name = `Acme_${Date.now()}`;
  let created;

  it('create profile', async () => {
    const { status, body } = await post('/webhook/creative/tools/style-management', {
      action: 'profile_create',
      profile: { name, guidelines: { tone: 'confident' } },
    });
    assert.strictEqual(status, 200);
    created = body.result?.[0] || body.result || body;
    assert.ok(created);
  });

  it('get profile by name', async () => {
    const { status, body } = await post('/webhook/creative/tools/style-management', {
      action: 'profile_get',
      name,
    });
    assert.strictEqual(status, 200);
    const got = body.result?.[0] || body.result || body;
    assert.ok(got);
  });

  it('update profile guidelines', async () => {
    const { status, body } = await post('/webhook/creative/tools/style-management', {
      action: 'profile_update',
      profile: { name, guidelines: { tone: 'confident', claims: 'no unverifiable claims' } },
    });
    assert.strictEqual(status, 200);
    const upd = body.result?.[0] || body.result || body;
    assert.ok(upd);
  });

  it('list profiles', async () => {
    const { status, body } = await post('/webhook/creative/tools/style-management', {
      action: 'profile_list',
      limit: 5,
      offset: 0,
    });
    assert.strictEqual(status, 200);
    assert.ok(body.result);
  });

  it('delete profile by name', async () => {
    const { status, body } = await post('/webhook/creative/tools/style-management', {
      action: 'profile_delete',
      name,
    });
    assert.strictEqual(status, 200);
    const del = body.result?.[0] || body.result || body;
    assert.ok(del);
  });
});
