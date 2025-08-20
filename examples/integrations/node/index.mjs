import process from 'node:process';

const BASE = (process.env.N8N_BASE_URL || 'http://localhost:5678').replace(/\/$/, '');
const API_KEY = process.env.N8N_API_KEY;
const USER = process.env.N8N_USER;
const PASS = process.env.N8N_PASS;

function authHeaders() {
  const h = { 'Content-Type': 'application/json' };
  if (API_KEY) {
    h['X-N8N-API-KEY'] = API_KEY;
  } else if (USER && PASS) {
    h['Authorization'] = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');
  }
  return h;
}

export async function listWorkflows() {
  const res = await fetch(`${BASE}/rest/workflows`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function planningAgent() {
  const payload = {
    project: { name: 'Website Revamp', methodology: 'agile' },
    tasks: [{ id: 'T1', skills: ['design'] }],
    resources: [{ name: 'Alice', skills: ['design'], capacity: 2 }],
  };
  const res = await fetch(`${BASE}/webhook/planning-agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const action = process.argv[2] || 'plan';
  try {
    if (action === 'list') {
      console.log(JSON.stringify(await listWorkflows(), null, 2));
    } else {
      console.log(JSON.stringify(await planningAgent(), null, 2));
    }
  } catch (e) {
    console.error(e);
    process.exit(1);
  }
}
