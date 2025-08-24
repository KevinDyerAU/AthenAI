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
  path.join(wfDir, 'quality-assurance-agent.json'),
  path.join(wfDir, 'qa-tools', 'automated-testing.json'),
  path.join(wfDir, 'qa-tools', 'compliance-checking.json'),
];

for (const f of files) {
  assert.ok(fs.existsSync(f), `Missing file: ${f}`);
  const json = readJSON(f);
  assert.ok(json.name, `Missing name in ${f}`);
  assert.ok(Array.isArray(json.nodes), `Missing nodes in ${f}`);
}

const toolsAuto = readJSON(files[1]);
const autoWebhook = toolsAuto.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(autoWebhook && autoWebhook.parameters && autoWebhook.parameters.path === 'qa/tools/automated-testing');

const toolsComp = readJSON(files[2]);
const compWebhook = toolsComp.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(compWebhook && compWebhook.parameters && compWebhook.parameters.path === 'qa/tools/compliance-checking');

const agent = readJSON(files[0]);
const agentWebhook = agent.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(agentWebhook && agentWebhook.parameters && agentWebhook.parameters.path === 'quality-assurance/run');

console.log('QA Agent workflow files are present and valid JSON.');
