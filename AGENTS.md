# Working in `agent-scripts`

This is a personal skill library for AI coding agents. Each subdirectory under `skills/` is a self-contained skill installable via `npx skills add jwmoss/agent-scripts`.

## Skill structure

```
skills/<skill-name>/
├── SKILL.md           # Entry point — required
├── references/        # Optional: deeper docs loaded on demand
├── scripts/           # Optional: executable helpers
└── evals/             # Optional: evals.json + trigger-loop artifacts
```

### Frontmatter

```yaml
---
name: skill-name                # kebab-case, ≤64 chars, must match directory
description: "What it does. When to use it. Trigger phrases."
allowed-tools: Read Grep Bash   # optional, restrict to needed tools
---
```

`description` is the routing signal — be concrete about when to use the skill and what triggers it. Vague descriptions lead to vague invocation.

### Naming

- **kebab-case** for skill and directory names.
- **Avoid**: `helper`, `utils`, `misc`, reserved words like `claude` or `anthropic`.
- **Prefer** action-oriented names: `sonarr` (manages Sonarr), `humanizer` (humanizes text).

## Authoring workflow

1. **Create** the skill skeleton — `skill-creator` walks through this.
2. **Audit** against the spec:
   ```sh
   skills/skill-checker/scripts/check-skill.sh skills/<name>
   ```
   Aim for `skills-ref: passed`. waza is advisory — long docs are fine if they earn their tokens.
3. **Evals** (optional but recommended for non-trivial skills): drop a trigger-loop or `evals/evals.json` in the skill directory.
4. **Commit** — `prek run` first; one logical change per commit; imperative subject ≤72 chars.

## Repo conventions

- **Secrets**: never commit. Reference 1Password items by name (e.g. `op item get "Sonarr unRAID"`) instead of pasting keys.
- **Internal hostnames/IPs are OK**: this is a personal repo; documenting `192.168.1.x` or `*.mossflix.com` in skill docs is expected.
- **Paths**: use `{baseDir}` placeholders inside skills, not hardcoded absolute paths.
- **Pre-commit**: `prek install` once per clone; hooks cover ruff, shellcheck, shfmt, yaml/json, whitespace.

## Reference skills in this repo

| Pattern | Look at |
|---|---|
| Minimal API wrapper | [`skills/radarr`](skills/radarr/), [`skills/sonarr`](skills/sonarr/) |
| Script-heavy + references | [`skills/skill-checker`](skills/skill-checker/) |
| Database query + analytics | [`skills/powerwall`](skills/powerwall/) |
| Multi-step authoring guide | [`skills/skill-creator`](skills/skill-creator/) |

## External resources

- [agentskills.io](https://agentskills.io) — open spec for agent skills
- [vercel-labs/skills](https://github.com/vercel-labs/skills) — the `npx skills` CLI
- [Anthropic: Agent Skills](https://code.claude.com/docs/en/skills) — Claude Code's skill docs
