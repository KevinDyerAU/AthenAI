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
  path.join(wfDir, 'development-agent.json'),
  path.join(wfDir, 'development-tools', 'code-generation.json'),
  path.join(wfDir, 'development-tools', 'testing-automation.json'),
  path.join(wfDir, 'development-tools', 'deployment-automation.json'),
];

for (const f of files) {
  assert.ok(fs.existsSync(f), `Missing file: ${f}`);
  const json = readJSON(f);
  assert.ok(json.name, `Missing name in ${f}`);
  assert.ok(Array.isArray(json.nodes), `Missing nodes in ${f}`);
}

// endpoints check
const toolsCodegen = readJSON(files[1]);
const codegenWebhook = toolsCodegen.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(codegenWebhook && codegenWebhook.parameters && codegenWebhook.parameters.path === 'development/tools/code-generation');

const toolsTesting = readJSON(files[2]);
const testingWebhook = toolsTesting.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(testingWebhook && testingWebhook.parameters && testingWebhook.parameters.path === 'development/tools/testing-automation');

const toolsDeploy = readJSON(files[3]);
const deployWebhook = toolsDeploy.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(deployWebhook && deployWebhook.parameters && deployWebhook.parameters.path === 'development/tools/deployment-automation');

const agent = readJSON(files[0]);
const agentWebhook = agent.nodes.find(n => n.type === 'n8n-nodes-base.webhook');
assert.ok(agentWebhook && agentWebhook.parameters && agentWebhook.parameters.path === 'development/run');

console.log('Development Agent workflow files are present and valid JSON.');
