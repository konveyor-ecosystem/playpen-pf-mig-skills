# Skill: Code Migration

A [Claude Code skill](https://code.claude.com/docs/en/skills) (also compatible with [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)) that orchestrates code migration using [Kantra](https://github.com/konveyor/kantra) static analysis, automated fixes, and visual regression testing. This skill delegates specialized tasks to [subagents](https://code.claude.com/docs/en/sub-agents).

## Prerequisites

- [Claude Code](https://code.claude.com/) or [Gemini CLI](https://geminicli.com/)
- [Kantra CLI](https://github.com/konveyor/kantra) installed and available on `$PATH`
- [Playwright MCP server](https://github.com/microsoft/playwright-mcp) configured (required for visual regression testing)
- Python 3 (for helper scripts)

## Setup

### Claude Code

1. Copy the `skills/code-migration/` directory to `.claude/skills/code-migration/` in your project (or `~/.claude/skills/code-migration/` for global availability).
2. Copy the `agents/` directory contents to `.claude/agents/` in your project (or `~/.claude/agents/` for global availability).
3. The skill is auto-discovered by Claude Code when relevant to your conversation, or invoke it directly with `/code-migration`.

See [Claude Code skills docs](https://code.claude.com/docs/en/skills) for more on skill placement and discovery.

### Gemini CLI

1. Copy the `skills/code-migration/` directory to `.gemini/skills/code-migration/` in your workspace (or `~/.gemini/skills/code-migration/` for global availability).
2. Copy the `agents/` directory contents to `.gemini/agents/` in your workspace (or `~/.gemini/agents/` for global availability).
3. **Uncomment the `tools:` section** in each agent `.md` file. Gemini CLI requires explicit tool declarations in the YAML frontmatter:
   ```yaml
   tools:
     - run_shell_command
     - list_directory
     - read_file
     - write_file
     - search_file_content
     - replace
     - glob
   ```
4. Enable experimental agents in your Gemini CLI settings:
   ```json
   {
     "experimental": {
       "enableAgents": true
     }
   }
   ```

See [Gemini CLI skills docs](https://geminicli.com/docs/cli/creating-skills/) and [subagents docs](https://geminicli.com/docs/core/subagents/) for more details.

## Subagents

This skill delegates specialized tasks to [subagents](https://code.claude.com/docs/en/sub-agents) ([Gemini equivalent](https://geminicli.com/docs/core/subagents/)):

| Subagent | Description |
|----------|-------------|
| `project-explorer` | Discovers project structure, build system, test commands, lint config |
| `kantra-command-builder` | Builds the correct `kantra analyze` flags for the project |
| `test-runner` | Runs test suites and reports results |
| `issue-analyzer` | Analyzes issues that persist across 3+ fix rounds |
| `visual-captures` | Discovers UI components and captures screenshots to a given directory |
| `visual-compare` | Compares baseline and post-migration screenshots, generates checkbox-tracked report |
| `visual-fix` | Fixes unchecked visual regression issues from the diff report |

## Usage

### Claude Code

Start a session in your project directory and ask Claude to migrate:

```
Migrate this project from PatternFly 5 to PatternFly 6
```

Or invoke the skill directly:

```
/code-migration PatternFly 5 to PatternFly 6
```

### Gemini CLI

```
Migrate this project from PatternFly 5 to PatternFly 6
```

Or use the skill explicitly:

```
/skills activate code-migration
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

- Subagents run in isolation with their own context window; they do not share conversation history with the main agent
- Subagents cannot spawn other subagents (no nesting)
- Gemini CLI subagents operate in YOLO mode (tools execute without individual confirmation) — exercise caution with destructive operations
- Gemini CLI requires explicit `tools:` declarations in agent frontmatter
- Gemini CLI requires `/tmp` directories to be added to context manually
- Claude Code subagents are loaded at session start; restart the session or use `/agents` after adding new agent files

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `scripts/kantra_output_helper.py` | Parses Kantra YAML output into summaries and per-file issue lists |
| `scripts/persistent_issues_analyzer.py` | Identifies issues that persist across multiple fix rounds |
