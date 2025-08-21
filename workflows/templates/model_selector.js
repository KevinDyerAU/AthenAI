// n8n Function node template: Model Selector
// Purpose: choose provider/model/params based on task metadata in the incoming item
// Usage: Place this node before Agent/LLM nodes. Downstream nodes can read fields from $json.model
// You can extend with routing logic based on task type, cost ceilings, latency, etc.

// Input item example:
// {
//   task: { type: 'analysis' | 'creative' | 'classification', priority: 'high'|'normal' },
//   constraints: { maxLatencyMs: 2000, maxCostUsd: 0.01 }
// }

const item = items[0] || { json: {} };
const task = item.json.task || {};
const constraints = item.json.constraints || {};

function pickModel(task) {
  const type = (task.type || '').toLowerCase();
  switch (type) {
    case 'creative':
      return { provider: 'openai', model: $env.OPENAI_MODEL || 'gpt-4o', temperature: 0.9 };
    case 'classification':
      return { provider: 'anthropic', model: $env.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20240620', temperature: 0.2 };
    case 'analysis':
    default:
      return { provider: 'openai', model: $env.OPENAI_MODEL || 'gpt-4o-mini', temperature: 0.3 };
  }
}

const choice = pickModel(task);

return [
  {
    json: {
      ...item.json,
      model: {
        provider: choice.provider,
        name: choice.model,
        temperature: choice.temperature,
        // Optional: add max tokens, top_p, etc.
      }
    }
  }
];
