# Skill: Code Migration (Inline)

A [Claude Code skill](https://code.claude.com/docs/en/skills) (also compatible with [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)) that orchestrates code migration using [Kantra](https://github.com/konveyor/kantra) static analysis, automated fixes, and visual regression testing. Unlike `code-migration`, this variant embeds all instructions directly in the skill file — **no subagents required**. Use this when your agent runtime supports skills but not subagents.

## Prerequisites

- [Claude Code](https://code.claude.com/) or [Gemini CLI](https://geminicli.com/)
- [Kantra CLI](https://github.com/konveyor/kantra) installed and available on `$PATH`
- [Playwright MCP server](https://github.com/microsoft/playwright-mcp) configured (required for visual regression testing)
- Python 3 (for helper scripts)

## Setup

### Claude Code

1. Copy the `skills/code-migration-inline/` directory to `.claude/skills/code-migration-inline/` in your project (or `~/.claude/skills/code-migration-inline/` for global availability).
2. No agent files are needed — all instructions are inline in the skill.

See [Claude Code skills docs](https://code.claude.com/docs/en/skills) for more on skill placement and discovery.

### Gemini CLI

1. Copy the `skills/code-migration-inline/` directory to `.gemini/skills/code-migration-inline/` in your workspace (or `~/.gemini/skills/code-migration-inline/` for global availability).
2. No agent files are needed.

See [Gemini CLI skills docs](https://geminicli.com/docs/cli/creating-skills/) for more details.

## When to Use This Variant

Use `code-migration-inline` instead of `code-migration` when:

- Your agent runtime supports skills but **not subagents** (e.g., older versions of Gemini CLI without `enableAgents`)
- You want a **single self-contained skill** with no external agent dependencies
- You prefer all instructions in one place for easier customization

The trade-off is that the inline skill consumes more context since all specialized instructions live in one file rather than being loaded on-demand by subagents.

## Usage

### Claude Code

Start a session in your project directory and ask Claude to migrate:

```
Migrate this project from PatternFly 5 to PatternFly 6
```

Or invoke the skill directly:

```
/code-migration-inline PatternFly 5 to PatternFly 6
```

### Gemini CLI

```
Migrate this project from PatternFly 5 to PatternFly 6
```

Or use the skill explicitly:

```
/skills activate code-migration-inline
```

## Migration Workspace

The skill creates a temporary workspace directory outside the project:

```bash
WORK_DIR=$(mktemp -d -t migration-$(date +%m_%d_%y_%H))
```

This directory (under `/tmp`) stores all migration artifacts: Kantra output, status files, screenshots, manifests, and reports.

### Gemini CLI: Add `/tmp` to Context

Gemini CLI requires directories to be added to context before the agent can access files in them. Since the migration workspace is created in `/tmp`, you need to add it to context early in the session. After the workspace is created, run:

```
/context add /tmp/migration-*
```

Or specify the exact path once the workspace directory is known.

## Target-Specific Guidance

Migration targets with additional pre/post-migration steps are defined in `targets/`. Currently available:

- [`targets/patternfly.md`](targets/patternfly.md) - PatternFly 5 to 6 migration with visual regression testing

## Workflow

The skill follows a 3-phase workflow:

1. **Discovery** - Explore project structure, build Kantra command, create workspace
2. **Fix Loop** - Iteratively fix issues in groups, validate after each round
3. **Final Validation** - Run E2E tests, execute visual regression loop (capture, compare, fix)

## Known Limitations

- All instructions are loaded into context at once, consuming more of the context window than the subagent variant
- Gemini CLI requires `/tmp` directories to be added to context manually
- The inline variant does not benefit from subagent isolation — verbose operations (like test output) stay in the main conversation context

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `scripts/kantra_output_helper.py` | Parses Kantra YAML output into summaries and per-file issue lists |
| `scripts/persistent_issues_analyzer.py` | Identifies issues that persist across multiple fix rounds |
