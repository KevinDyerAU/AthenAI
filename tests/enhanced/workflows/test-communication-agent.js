const fs = require('fs');
const path = require('path');
const assert = require('assert');

function readJSON(p) {
  const raw = fs.readFileSync(p, 'utf8');
  return JSON.parse(raw);
}

const root = path.resolve(__dirname, '../../');
const wfDir = path.join(root, 'workflows');

const files = [
  path.join(wfDir, 'communication-agent.json'),
  path.join(wfDir, 'communication-tools', 'email-delivery.json'),
  path.join(wfDir, 'communication-tools', 'social-media.json'),
];

for (const f of files) {
  assert.ok(fs.existsSync(f), `Missing file: ${f}`);
  const json = readJSON(f);
  assert.ok(json.name, `Missing name in ${f}`);
  assert.ok(Array.isArray(json.nodes), `Missing nodes in ${f}`);
}

const toolsEmail = readJSON(files[1]);
const emailWebhook = toolsEmail.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(emailWebhook && emailWebhook.parameters && emailWebhook.parameters.path === 'communication/tools/email-delivery');

const toolsSocial = readJSON(files[2]);
const socialWebhook = toolsSocial.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(socialWebhook && socialWebhook.parameters && socialWebhook.parameters.path === 'communication/tools/social-media');

const agent = readJSON(files[0]);
const agentWebhook = agent.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(agentWebhook && agentWebhook.parameters && agentWebhook.parameters.path === 'communication/run');

console.log('Communication Agent workflow files are present and valid JSON.');
