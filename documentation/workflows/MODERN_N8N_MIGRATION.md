# Modern n8n Integration Migration (v1.19.4+)

This guide migrates legacy workflows that used community packages (e.g., `@n8n/n8n-nodes-langchain`) to modern built-in AI capabilities and Tools Agent patterns.

## Goals
- Use built-in AI Agent nodes (native `n8n-nodes-langchain.*`).
- Adopt Tools Agent approach for AI tools.
- Enable Node-as-Tools: dynamic access to n8n's node catalog.
- Use built-in conversation memory.
- Support dynamic model selection across providers.

## Key Concepts
- Tools Agent: Agent node with a set of tools (HTTP Request, Function, AI tools, etc.).
- Conversation Memory: use n8n memory features; configure persistence per workflow.
- Model Selection: choose provider/model via credentials and parameters; route based on task type.

## Migration Steps
1. Inventory your workflows with `scripts/n8n/validate_modern_n8n.py`.
2. Run `scripts/n8n/migrate_to_builtins.py --in-place` to auto-rewrite common patterns.
3. Review diffs and import into n8n. Replace community Agent nodes with built-in Agent nodes.
4. Configure Tools Agent with a curated set of tools from the Tools Registry JSON.
5. Enable conversation memory in Agent nodes as needed (short/long memory, window size).
6. Configure credentials for AI providers (OpenAI, Anthropic, etc.).

## Node-as-Tools Registry
- Build/update registry:
```
python scripts/n8n/build_tools_registry.py --output workflows/tools_registry.json
```
- The registry provides semantic descriptions for tools and suggested usage.
- Agents can consult the registry (via Code node or external service) to select tools.

## Testing
- Validate zero community deps:
```
python scripts/n8n/validate_modern_n8n.py --workflows-dir workflows
```
- Run integration tests hitting API:
```
python tests/integration/api_flows_test.py
```

## Docker Compose Notes
- Remove any custom extension mounts for community nodes.
- Ensure `N8N_VERSION >= 1.19.4` and no `N8N_CUSTOM_EXTENSIONS` volumes referencing community packages.

## Troubleshooting
- Agent not using tools: verify Tools list and registry entries; check credentials.
- Memory not persisting: ensure memory enabled in agent and persistence configured in n8n.
- Model errors: verify provider credentials and rate limits.
