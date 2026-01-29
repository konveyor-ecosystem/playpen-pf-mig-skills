---
name: code-migration
description: Migrate applications between technology stacks using Kantra static analysis. Use when migrating Java, Node.js, Python, Go, or .NET applications, upgrading frameworks, modernizing codebases, dependency upgrades, or framework version upgrades. Keywords: kantra, source code migration, technology migration.
---

# Code Migration with Kantra

Supported providers: java, nodejs, python, go, dotnet

## Setup and Discovery

Delegate project discovery to the project-explorer sub-agent to identify:
- Build system and build command
- Test suites and test commands
- Lint configuration and lint command

Create a migration workspace directory **outside** the application directory (e.g., `/tmp/migration-workspace-<app-name>/`).

Check for target-specific instructions at `targets/<target>.md` and follow that guidance first.

## Migration Workflow Checklist

Copy this to track progress:

```
Migration Progress:
- [ ] Project discovery complete
- [ ] Initial Kantra analysis
- [ ] Fix plan created
- [ ] Fixes applied
- [ ] Validation passed (Kantra + build + tests)
- [ ] Exit criteria met
```

## Migration Loop

Execute iteratively until exit criteria are met:

### 1. Run Analysis

```bash
kantra analyze --input <project_path> --target <target1> --target <target2> --output <work_dir>/kantra-output --provider <provider>
```

Options:
- Add `--rules <path>` for custom rules
- Add `--enable-default-rulesets=false` to disable default rules

### 2. Parse Results

Use bundled script to analyze Kantra output (returns JSON by default):

```bash
python scripts/kantra_output_helper.py analyze <work_dir>/kantra-output/output.yaml
```

This returns structured JSON with:
- `total_issues`: Total count of distinct issues
- `issues`: List of issues with rule_id, description, file_count, and affected files

### 3. Plan Fixes

**IMPORTANT**: Do NOT group by simple metrics like file_count, severity, or effort alone.

Create detailed fix plan in `<workspace>/plan.md` by analyzing interdependencies:

#### a) Identify Interdependencies

For each issue, analyze:
- **What other issues does this relate to?** (same subsystem, same file, similar changes)
- **What must be fixed before this?** (e.g., can't fix API usage until imports are updated)
- **What will this break if fixed first?** (will fixing imports cause build failures?)
- **Which issues should be fixed together?** (minimize back-and-forth changes)

#### b) Create Logical Groups

Group issues that:
- Affect the same architectural layer or subsystem
- Have dependency relationships (fix A enables fixing B)
- Minimize rework (avoid fixing something that will break when you fix something else later)

NOT based on: file_count, severity labels, or prescribed categories

#### c) Order Groups to Minimize Iterations

Sequence groups so:
- Foundation changes come before dependent changes
- Each group's fixes don't create new issues for previous groups
- Build remains functional after each group (when possible)

#### d) Document Plan

Use this template:

```markdown
# Migration Plan

## Issues Analysis
[What patterns you identified, what subsystems are affected]

## Fix Groups (in order)

### Group 1: [Name]
**Rationale**: [Why these issues are grouped and why this group is first]
**Issues**: [rule-id-1, rule-id-2, ...]
**Dependencies**: [What this group depends on, what depends on this]
**Files affected**: [list]

### Group 2: [Name]
**Rationale**: [Why this comes after Group 1]
...
```

Identify additional issues beyond Kantra: breaking changes, deprecated APIs, dependency conflicts.

Update plan.md as you progress through iterations.

### 4. Apply Fixes and Validate

Apply fixes following your plan, then validate:

a) Re-run Kantra analysis to verify issue count decreased

b) Run build to ensure no compilation errors

c) Run lint to catch code quality issues

d) Delegate to test-runner sub-agent (executes tests in priority order: behavioral/E2E → integration → unit)

e) Compare issue counts to previous round - if no progress, reassess approach

### 5. Exit Decision

**Exit criteria (ALL must be true):**
- Kantra analysis reports 0 issues
- Build succeeds
- All tests pass
- No known unfixed migration issues remain

**If criteria NOT met:** Continue to next iteration.

**If an issue cannot be fixed:**
- Attempt at least 2 different approaches before marking unfixable
- Document why it cannot be fixed automatically
- Continue fixing other issues
- Only exit after ALL fixable issues are resolved AND unfixable ones are documented

## Analyzing Persistent Issues

If issues remain unfixed after multiple iterations, delegate to issue-analyzer sub-agent.

The sub-agent will identify issues appearing 3+ times and recommend:
- False positives to ignore
- Unfixable issues to document and skip
- Fixable issues requiring different approaches

Focus efforts on fixable issues only.

## Guidelines

- **Focus on logical grouping**: Identify interdependent issues and fix them in optimal order
- **Be systematic**: Follow your planned fix order rather than addressing issues randomly
- **Be thorough**: Verify each fix doesn't break existing features
