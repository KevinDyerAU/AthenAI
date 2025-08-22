import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

const findRepoRoot = () => {
  let currentDir = process.cwd();
  while (currentDir !== '/' && !fs.existsSync(path.join(currentDir, '.git'))) {
    currentDir = path.dirname(currentDir);
  }
  return currentDir;
};

const policiesPath = path.join(findRepoRoot(), 'infrastructure/security/rbac/policies.yaml');

function fail(msg) {
  console.error(`[RBAC] Validation failed: ${msg}`);
  process.exit(1);
}

function loadYaml(file) {
  try {
    return yaml.load(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    fail(`Cannot read YAML at ${file}: ${e.message}`);
  }
}

function ensureArray(name, v) {
  if (!Array.isArray(v)) fail(`${name} must be an array`);
}

function validate() {
  if (!fs.existsSync(policiesPath)) fail(`policies file missing at ${policiesPath}`);
  const doc = loadYaml(policiesPath);
  if (!doc || typeof doc !== 'object') fail('policies YAML is empty or invalid');
  if (doc.version !== 1) fail('version must be 1');
  ensureArray('roles', doc.roles);

  const roleNames = new Set();
  for (const role of doc.roles) {
    if (!role.name || typeof role.name !== 'string') fail('role.name missing or not a string');
    if (roleNames.has(role.name)) fail(`duplicate role name: ${role.name}`);
    roleNames.add(role.name);
    ensureArray(`role.allow for ${role.name}`, role.allow);
    for (const rule of role.allow) {
      if (!rule.resource || typeof rule.resource !== 'string') fail(`rule.resource missing for ${role.name}`);
      if (!Array.isArray(rule.actions) || rule.actions.length === 0) fail(`rule.actions missing for ${role.name}`);
      for (const a of rule.actions) {
        if (typeof a !== 'string') fail(`non-string action in ${role.name}`);
      }
    }
  }

  console.log('[RBAC] policies.yaml is valid.');
}

validate();
