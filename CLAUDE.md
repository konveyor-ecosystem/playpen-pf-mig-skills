# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is an experimental playpen for prototyping AI agent skills and tools that assist with migrating PatternFly 5 (PF5) codebases to PatternFly 6 (PF6). The focus is exploratory and educational.

## What Belongs Here

- Agent prompts, workflows, and evaluation harnesses
- Scripts and tooling for migration experiments
- Notes and findings from migration trials
- Small, focused proof-of-concepts for automated refactoring

## Guidelines for Contributions

When adding experiments or skills:
- Keep contributions small and focused on a single migration pattern or agent capability
- Include context or notes explaining what was learned
- This is not a production toolchain - prioritize learning over polish

## Code Migration Skill / Recipe

The code migration workflow is implemented across three parallel systems targeting different agent runtimes. These must be kept in sync.

### Mapping

| Goose (recipes) | Claude Code / Gemini (skills + agents) | Inline skill |
|-----------------|----------------------------------------|--------------|
| `goose/recipes/migration.yaml` | `skills/code-migration/SKILL.md` | `skills/code-migration-inline/SKILL.md` |
| `goose/recipes/subrecipes/*.yaml` | `agents/*.md` | Instructions inlined in SKILL.md and `targets/` |
| `goose/recipes/targets/*.md` | `skills/code-migration/targets/*.md` | `skills/code-migration-inline/targets/*.md` |
| `goose/recipes/scripts/*.py` | `skills/code-migration/scripts/*.py` | `skills/code-migration-inline/scripts/*.py` |

- **Recipes** ([docs](https://block.github.io/goose/docs/guides/recipes/recipe-reference)) are Goose YAML files with Jinja templates (`{{ param }}`), `prompt:` / `instructions:` sections, and typed `parameters:`.
- **Subrecipes** ([docs](https://block.github.io/goose/docs/guides/recipes/subrecipes)) are child recipes invoked via the `subagent` tool. They have structured parameter passing via `values:`.
- **Skills** ([Claude docs](https://code.claude.com/docs/en/skills), [Gemini docs](https://geminicli.com/docs/cli/skills/)) are `SKILL.md` markdown files with YAML frontmatter. No Jinja templates.
- **Agents / Subagents** ([Claude docs](https://code.claude.com/docs/en/sub-agents), [Gemini docs](https://geminicli.com/docs/core/subagents/)) are markdown files in `agents/`. They receive information via natural language from the main agent, not structured parameters.
- **Inline skill** (`code-migration-inline`) has all subagent instructions embedded directly in SKILL.md and `targets/`. Use this when the runtime supports skills but not subagents.

### Propagating Changes

When modifying any code-migration file, propagate the change to its counterparts:

1. **Subrecipe changed** → Update the corresponding `agents/*.md` file. Adapt Jinja templates to natural language. Remove recipe-specific constructs (`{{ }}`, `prompt:` / `instructions:` split, `values:`).
2. **Agent changed** → Update the corresponding `goose/recipes/subrecipes/*.yaml` file. Add Jinja parameter references where the agent uses natural language inputs.
3. **Main recipe changed** → Update `skills/code-migration/SKILL.md`. Recipe uses `subagent` tool invocations; skill uses "Delegate to `<name>` subagent" with natural language descriptions of inputs.
4. **Skill changed** → Update `goose/recipes/migration.yaml`.
5. **Target file changed** (e.g., `patternfly.md`) → Update all three copies: `goose/recipes/targets/`, `skills/code-migration/targets/`, `skills/code-migration-inline/targets/`. The recipe version uses `Invoke <subrecipe> sub-recipe with:` and key-value params. The skill version uses `Delegate to <subagent> subagent with:` and natural language descriptions. The inline version has full procedural instructions with no delegation.
6. **Script changed** → Update all three copies: `goose/recipes/scripts/`, `skills/code-migration/scripts/`, `skills/code-migration-inline/scripts/`.

### Key Differences Between Formats

- **Subagent inputs are not structured.** Agents receive all context as natural language from the delegating agent. Describe inputs naturally (e.g., "the workspace directory path, the dev server command from project discovery") rather than as key-value pairs.
- **Recipe subrecipes use structured parameters** with `values:` mapping and Jinja substitution.
- **Gemini CLI agents** require explicit `tools:` in YAML frontmatter (comment out; users are supposed to uncomment when they use the skill).

### Style Rules for Instructions

- Use `**bold**` for emphasis on behavioral instructions the agent must follow (e.g., `**Do not skip any discoverable element.**`). Do not remove these when editing.
- Keep instructions succinct and unambiguous.
- Use the term "subagent" explicitly when delegating (e.g., "Delegate to `visual-fix` subagent with...").