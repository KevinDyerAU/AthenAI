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
  path.join(wfDir, 'planning-agent.json'),
  path.join(wfDir, 'planning-tools', 'resource-allocation.json'),
  path.join(wfDir, 'planning-tools', 'timeline-optimization.json'),
];

for (const f of files) {
  assert.ok(fs.existsSync(f), `Missing file: ${f}`);
  const json = readJSON(f);
  assert.ok(json.name, `Missing name in ${f}`);
  assert.ok(Array.isArray(json.nodes), `Missing nodes in ${f}`);
}

const toolsAlloc = readJSON(files[1]);
const allocWebhook = toolsAlloc.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(allocWebhook && allocWebhook.parameters && allocWebhook.parameters.path === 'planning/tools/resource-allocation');

const toolsTimeline = readJSON(files[2]);
const tlWebhook = toolsTimeline.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(tlWebhook && tlWebhook.parameters && tlWebhook.parameters.path === 'planning/tools/timeline-optimization');

const agent = readJSON(files[0]);
const agentWebhook = agent.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(agentWebhook && agentWebhook.parameters && agentWebhook.parameters.path === 'planning/run');

console.log('Planning Agent workflow files are present and valid JSON.');
