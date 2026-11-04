# Connect your AI Agent

The skill loop needs one MCP server: Evaboot. Steps 0 to 2 use it: the quota check, the export, and `get_export` to read it.

## 1. Account

An [Evaboot account](https://dash.evaboot.com/accounts/signup/?last_click_origin=prospecting-skills-repo) with credits, and a Sales Navigator seat connected to it through the Evaboot Chrome extension.

## 2. Get the repo

```bash
git clone https://github.com/evaboot-labs/prospecting-skills
cd prospecting-skills
cp .env.example .env
```

## 3. Connect the Evaboot MCP

**Claude Code:** write your key from [dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/) into `.env` as `EVABOOT_API_KEY`, load it (`set -a; . ./.env; set +a`), then start Claude Code from this folder. It reads `.mcp.json` and asks you to approve the `evaboot` server. Or sign in with a Claude account that already has the Evaboot connector (*Settings > Connectors > Add custom connector*, URL `https://mcp.evaboot.com/mcp`).

**Claude Code plugin** (installed with `/plugin install`, no clone): export your key before you start Claude Code, `export EVABOOT_API_KEY=<your key>`. Without it the `evaboot` server does not connect.

**Codex, Cursor:** add `https://mcp.evaboot.com/mcp` as an HTTP MCP server with the header `Authorization: Bearer <your key>`. The skills in `skills/` are plain SKILL.md files, so these agents run the same loop.

## 4. Check

Ask your AI Agent: "Check my Evaboot quota and whether my Sales Navigator is connected." Then ask: "Which skills can you use in this folder?" It must list `prospecting-skills`, `define-icp-and-value-prop`, `qualify-leads`, `buying-signal-scoring`, `write-outreach-messages`, `draft-outreach` and `account-research`.

Back to the [README](../README.md).
