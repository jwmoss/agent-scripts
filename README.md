# agent-scripts

A personal skill library for AI coding agents — Claude Code, Codex, Cursor, OpenCode, Gemini CLI, and more — covering home-lab automation (Plex/Sonarr/Radarr stack, Tesla Powerwall), skill authoring, and developer tooling.

## Installation

Skills are installed with [`skills`](https://github.com/vercel-labs/skills), the open agent-skills CLI.

### Install everything globally for all agents

```sh
npx skills add jwmoss/agent-scripts --all -g -y
```

This drops every skill into `~/.agents/skills/<name>/` and links it into every installed agent (Claude Code, Codex, Cursor, OpenCode, Cline, Continue, Gemini CLI, GitHub Copilot, Antigravity, OpenClaw, and others — auto-detected).

### Install specific skills

```sh
# One or more by name
npx skills add jwmoss/agent-scripts --skill sonarr --skill radarr -g -y

# Browse without installing
npx skills add jwmoss/agent-scripts --list
```

### Flag reference

| Flag | Effect |
|------|--------|
| `-g, --global` | Install into the user-global location (`~/.agents/skills/`) instead of the current project |
| `-a, --agent <name>` | Restrict to specific agents (e.g. `-a claude-code -a codex`). Omit to install for **all** detected agents |
| `--skill <name>` | Install a specific skill (repeatable). Use `'*'` for all |
| `--all` | Install every skill to every agent without prompts |
| `-y, --yes` | Skip confirmation prompts (CI-friendly) |
| `--copy` | Copy files instead of symlinking |

### Local development

```sh
git clone git@github.com:jwmoss/agent-scripts.git
cd agent-scripts
npx skills add . -g -y    # install from local checkout
```

## Available Skills

### Media Server (Mossflix)

| Skill | Description |
|-------|-------------|
| [sonarr](skills/sonarr/) | Manage TV series in Sonarr — add/remove shows, search the library, kick off downloads |
| [radarr](skills/radarr/) | Manage movies in Radarr — search, add, push releases, manual import |
| [jellyseerr](skills/jellyseerr/) | Request movies and TV via the Jellyseerr API |
| [tracearr](skills/tracearr/) | Active streams, user activity, account-sharing violations, and playback history from Tracearr |
| [tautulli](skills/tautulli/) | Plex viewing analytics — watch time, popular content, transcode rates, concurrent streams |

### Smart Home / Energy

| Skill | Description |
|-------|-------------|
| [powerwall](skills/powerwall/) | Query Tesla Powerwall data from InfluxDB — solar production, grid usage, battery state, self-sufficiency |

### Skill Authoring

| Skill | Description |
|-------|-------------|
| [skill-creator](skills/skill-creator/) | Guide for creating new skills or iterating existing ones with evals |
| [skill-checker](skills/skill-checker/) | Audit SKILL.md against agentskills.io spec, waza budget, and eval-evidence checks |

### Development

| Skill | Description |
|-------|-------------|
| [modern-python](skills/modern-python/) | Modern Python project setup with uv, ruff, and pytest (vendored from [trailofbits/skills](https://github.com/trailofbits/skills/tree/main/plugins/modern-python)) |

### Writing

| Skill | Description |
|-------|-------------|
| [humanizer](skills/humanizer/) | Strip AI-isms from prose — em-dash overuse, rule-of-three, promotional vocabulary, vague attributions (submodule from [blader/humanizer](https://github.com/blader/humanizer)) |

## Contributing

This is a personal repo, but PRs that fix bugs or add useful skills are welcome.

Before pushing, run the hooks:

```sh
prek install   # one-time, installs git hooks
prek run       # run on staged changes
```

See [`.pre-commit-config.yaml`](.pre-commit-config.yaml) for the configured hooks (ruff, shellcheck, shfmt, yaml/json validation, whitespace).

### Adding a new skill

1. Create `skills/<name>/SKILL.md` with valid frontmatter (`name`, `description`).
2. Audit it: `skills/skill-checker/scripts/check-skill.sh skills/<name>`.
3. Open a PR.

## License

See [LICENSE](LICENSE).
