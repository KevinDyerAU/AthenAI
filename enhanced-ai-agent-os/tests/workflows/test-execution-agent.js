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
  path.join(wfDir, 'execution-agent.json'),
  path.join(wfDir, 'execution-tools', 'parallel-processing.json'),
  path.join(wfDir, 'execution-tools', 'error-recovery.json'),
];

for (const f of files) {
  assert.ok(fs.existsSync(f), `Missing file: ${f}`);
  const json = readJSON(f);
  assert.ok(json.name, `Missing name in ${f}`);
  assert.ok(Array.isArray(json.nodes), `Missing nodes in ${f}`);
}

const toolsParallel = readJSON(files[1]);
const parWebhook = toolsParallel.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(parWebhook && parWebhook.parameters && parWebhook.parameters.path === 'execution/tools/parallel-processing');

const toolsRecovery = readJSON(files[2]);
const recWebhook = toolsRecovery.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(recWebhook && recWebhook.parameters && recWebhook.parameters.path === 'execution/tools/error-recovery');

const agent = readJSON(files[0]);
const agentWebhook = agent.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(agentWebhook && agentWebhook.parameters && agentWebhook.parameters.path === 'execution/run');

console.log('Execution Agent workflow files are present and valid JSON.');
