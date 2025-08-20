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
  path.join(wfDir, 'analysis-agent.json'),
  path.join(wfDir, 'analysis-tools', 'statistical-analysis.json'),
  path.join(wfDir, 'analysis-tools', 'data-visualization.json'),
];

for (const f of files) {
  assert.ok(fs.existsSync(f), `Missing file: ${f}`);
  const json = readJSON(f);
  assert.ok(json.name, `Missing name in ${f}`);
  assert.ok(Array.isArray(json.nodes), `Missing nodes in ${f}`);
}

// basic checks for endpoints
const toolsStat = readJSON(files[1]);
const statWebhook = toolsStat.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(statWebhook && statWebhook.parameters && statWebhook.parameters.path === 'analysis/tools/statistical-analysis');

const toolsViz = readJSON(files[2]);
const vizWebhook = toolsViz.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
ah = vizWebhook && vizWebhook.parameters && vizWebhook.parameters.path === 'analysis/tools/data-visualization';
assert.ok(ah);

const agent = readJSON(files[0]);
const agentWebhook = agent.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(agentWebhook && agentWebhook.parameters && agentWebhook.parameters.path === 'analysis/run');

console.log('Analysis Agent workflow files are present and valid JSON.');
