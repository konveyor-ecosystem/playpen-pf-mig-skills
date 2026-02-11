# Playpen: PatternFly 5 to 6 Migration Agent Skills and Tools

This repository is a **playpen for small, focused experiments** related to migrating PatternFly 5 (PF5) codebases to PatternFly 6 (PF6) using AI-driven coding agents and agent skills.

The intent is exploratory and educational rather than production-ready.

## Purpose

The goals of this repository are to:

- Prototype **agent skills, prompts, and workflows** that assist with PatternFly migrations
- Capture **proofs of concept (PoCs)** for automated or semi-automated refactoring approaches

## Migration Skills and Recipes

This repository contains migration tooling for multiple agent runtimes:

| Path | Runtime | Description |
|------|---------|-------------|
| [`goose/recipes/`](goose/recipes/README.md) | [Goose](https://github.com/block/goose) | Recipe with subrecipes for migration orchestration |
| [`skills/code-migration/`](skills/code-migration/README.md) | [Claude Code](https://code.claude.com/) / [Gemini CLI](https://geminicli.com/) | Skill with subagents for migration orchestration |
| [`skills/code-migration-inline/`](skills/code-migration-inline/README.md) | [Claude Code](https://code.claude.com/) / [Gemini CLI](https://geminicli.com/) | Self-contained skill (no subagents) for runtimes without subagent support |

See each README for setup instructions, prerequisites, and usage examples.

## Scope

Typical contents include:

- Agent prompts, workflows, and evaluation harnesses
- Scripts and tooling for migration experiments
- Notes, findings, and lessons learned from migration trials

This repository is **not** a reference implementation, supported toolchain, or official PatternFly migration guide. Approaches explored here may be incomplete, opinionated, or intentionally experimental.

## Status

This repository is **experimental and volatile**. Content may change frequently as migration strategies, agent capabilities, and PatternFly guidance evolve.

## Contributing

Contributions are welcome if they:

- Are small and focused
- Clearly demonstrate a migration pattern or agent capability
- Include context or notes explaining what was learned

## Third-Party Notices

This project encourages reuse and attribution of open source software.

Details of third-party code and licenses used in this repository can be found in
[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md).

## Code of Conduct

Refer to Konveyor's Code of Conduct
[here](https://github.com/konveyor/community/blob/main/CODE_OF_CONDUCT.md).
