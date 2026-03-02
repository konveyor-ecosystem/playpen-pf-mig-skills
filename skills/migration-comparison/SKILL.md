---
name: migration-comparison
description: Compare two migration attempts of the same codebase using AST and text diffing. Accepts git repos or local paths and generates an HTML comparison report. Keywords: compare, diff, migration, comparison, report.
---

# Migration Comparison

Compare two different migration attempts of the same codebase (e.g., AI agent A vs ground truth, or agent A vs agent B). Produces a self-contained HTML comparison report with categorized changes, semantic analysis, and side-by-side diffs.

---

## Phase 1: Setup & Validation

### 1. Collect Inputs

Ask the user for:
- **Reference A**: git URL with branch (e.g., `https://github.com/org/repo@branch`) or a local directory path. Ask for a label (e.g., "Ground Truth", "Agent A").
- **Reference B**: same format. Ask for a label.
- **File filters** (optional): glob patterns to restrict which files are compared (e.g., `*.tsx`, `src/**/*.ts`).

### 2. Create Workspace

Create a temporary workspace directory outside either project:

```bash
WORK_DIR=$(mktemp -d -t migration-comparison-$(date +%m_%d_%y_%H))
```

All artifacts go inside `$WORK_DIR`.

### 3. Validate Inputs

For each reference (A and B):

**If local path:**
- Verify the directory exists and contains files.
- **If the path is invalid or empty, tell the user what is wrong and ask them to provide a corrected path.**

**If git URL:**
- Attempt: `git clone --branch <branch> --depth 1 <url> $WORK_DIR/<label>`
- **If the clone fails** (auth error, invalid URL, branch not found, network issue), show the user the error and ask:
  1. Provide a corrected URL/branch
  2. Provide a local path instead
  3. Abort
- **If the branch is not found**, run `git ls-remote --heads <url>` to list available branches and show them to the user.

### 4. Check Tool Availability

Run:
```bash
python3 scripts/run_diffs.py --check-gumtree
```

This returns JSON: `{"available": true/false, "method": "native|podman|docker|none", "version": "..."}`.

**If GumTree is not available**, inform the user and ask:
1. Continue with text-only diffing (still produces a useful report, just without AST-level semantic categorization)
2. Install GumTree first (`podman pull gumtreediff/gumtree`, `docker pull gumtreediff/gumtree`, or download from [GitHub releases](https://github.com/GumTreeDiff/gumtree/releases))
3. Abort

Record the user's choice for Phase 2.

### 5. Verify Repos Are Comparable

Run:
```bash
python3 scripts/enumerate_files.py <dir_a> <dir_b> --check-only
```

This prints overlap stats. **If the two trees have zero overlapping files**, warn the user:

> "These repos share no common files — are you sure you want to compare them?"

Ask to proceed or provide different inputs.

---

## Phase 2: Diff Analysis

Delegate to `repo-differ` subagent with:
- The workspace directory path (`$WORK_DIR`)
- The paths to both directories (local paths or cloned repo paths)
- The labels for each reference
- Whether GumTree is available (and the method: native or docker)
- File filter globs (if provided)

The subagent runs the full pipeline: `enumerate_files.py` → `run_diffs.py` → `categorize_changes.py` and produces `comparison-data.json`.

**If the subagent reports errors** (e.g., too many diff failures, systemic GumTree issues), surface them to the user and ask whether to continue to report generation or investigate.

---

## Phase 3: Report

Delegate to `comparison-report-generator` subagent with:
- The workspace directory path
- The labels for each reference

The subagent reads `comparison-data.json`, annotates the most significant changes with migration-context descriptions, and generates `comparison-report.html`.

---

## Phase 4: Output

Tell the user the path to the generated report:

```
Comparison report: $WORK_DIR/comparison-report.html
```

---

## Guidelines

- **Validate before proceeding** — never silently skip a broken input.
- **Ask the user when something goes wrong** — don't guess or abort without asking.
- **GumTree is optional** — the skill works with text-only diffing. GumTree adds richer AST-level categorization but is not required.
- **Keep the workspace clean** — all outputs go in `$WORK_DIR`.
