# Compound Engineering for Hermes Agent

A Hermes Agent plugin port of [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — the compound engineering methodology with 31 skills and 39+ agent personas.

This fork tracks upstream and adds Hermes-specific adaptations at load time. The upstream `skills/` directory is kept untouched for clean merges.

## Install

```bash
hermes plugins install christianpound/compound-engineering-hermes
```

Then restart Hermes (or `/reset` in an existing session). The skills appear as slash commands:

```
/ce-brainstorm make background job retries safer
/ce-plan
/ce-work
/ce-code-review
/ce-compound
```

List all skills:

```
/skills
```

List available agent personas:

```
/ce-agents
```

Load a specific agent's prompt:

```
/ce-agent ce-adversarial-reviewer
```

## What this fork does

The upstream plugin is authored for Claude Code with converters for 12+ other platforms. This fork adds Hermes as a 13th target via three files:

| File | Purpose |
|------|---------|
| `plugin.yaml` | Hermes plugin manifest |
| `__init__.py` | Registers all 31 skills as slash commands + `/ce-agents` and `/ce-agent` commands |
| `transform_hermes.py` | Rewrites Claude Code-specific references to Hermes equivalents at load time |

### Content transforms

At registration time, skill content is transformed:

| Claude Code | Hermes Agent |
|---|---|
| `~/.claude/` | `~/.hermes/` |
| `AskUserQuestion` / `clarify` via `ToolSearch` | `clarify` (native in Hermes) |
| `TaskCreate`/`TaskUpdate`/`TaskList` | `todo` tool |
| `delegate_task`/`delegate_task` | `delegate_task` |
| `CLAUDE_SKILL_DIR` | `~/.hermes/plugins/compound-engineering` |

The upstream skills already enumerate multiple platforms (Claude Code, Codex, Antigravity, Pi) — Hermes is inserted into those same lists, not substituted.

### Skill category

Skills are installed under `~/.hermes/skills/software-development/compound-engineering/` so Hermes groups them under the **software-development** category in the skills list, consistent with other development skills.

## Update from upstream

This fork automatically syncs with upstream daily via a GitHub Action (`.github/workflows/sync-upstream.yml`). To manually update:

```bash
git remote add upstream https://github.com/EveryInc/compound-engineering-plugin.git
git fetch upstream
git merge upstream/main
git push
```

The Hermes-specific files (`plugin.yaml`, `__init__.py`, `transform_hermes.py`) live at the repo root and don't conflict with upstream's `src/` converters.

## Skills

31 skills covering the full compound engineering loop:

| Skill | Purpose |
|---|---|
| `/ce-ideate` | Generate and critically evaluate grounded ideas |
| `/ce-brainstorm` | Explore requirements and write a requirements-only plan |
| `/ce-plan` | Enrich requirements into implementation-ready plans |
| `/ce-work` | Execute plans with native or cross-model implementation |
| `/ce-simplify-code` | Refine freshly written code for clarity and reuse |
| `/ce-code-review` | Multi-agent review against the plan before merging |
| `/ce-compound` | Capture learnings into `docs/solutions/` |
| `/ce-debug` | Reproduce, trace root cause, fix bugs |
| `/ce-strategy` | Create and maintain `STRATEGY.md` |
| `/lfg` | Full autonomous shipping pipeline |
| ... | 21 more skills |

Run `/skills` after install to see the full list.

## License

MIT — same as upstream.

## Credits

- [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) by Kieran Klaassen and Trevin Chow
- Hermes adaptation by [christianpound](https://github.com/christianpound)