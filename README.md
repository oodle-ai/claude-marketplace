# Oodle Plugins

Claude Code plugin marketplace by [Oodle AI](https://github.com/oodle-ai).

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [create-pr](plugins/create-pr/) | Intelligent PR creation with observability enforcement |

## Installation

Add the marketplace:

```bash
/plugin marketplace add https://github.com/oodle-ai/claude-marketplace.git
```

Install a plugin:

```bash
/plugin install create-pr
```

To update the marketplace and get the latest plugins:

```bash
/plugin marketplace update oodle-plugins
```

After installing or updating a plugin, reload to apply:

```bash
/reload-plugins
```

## Adding a New Plugin

1. Create `plugins/<plugin-name>/` with a `.claude-plugin/plugin.json` manifest.
2. Add skills, hooks, commands, or agents under the plugin directory.
3. Add an entry to `.claude-plugin/marketplace.json`.
4. Add a row to the table above.

See [Plugin Structure](https://docs.claude.com/en/docs/claude-code/plugins) for the full spec.

## License

Apache-2.0
