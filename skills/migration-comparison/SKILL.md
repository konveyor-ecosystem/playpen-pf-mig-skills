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
- **Migration target** (optional): identifier for target-specific pattern scoring (e.g., `patternfly`). When specified, the scoring step uses target-specific pattern detectors for more precise quality scoring.

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
- The migration target (if provided, e.g., `patternfly`)

The subagent runs the full pipeline: `enumerate_files.py` → `run_diffs.py` → `categorize_changes.py` → `score_migration.py` and produces `comparison-data.json` and `scoring-results.json`.

**If the subagent reports errors** (e.g., too many diff failures, systemic GumTree issues), surface them to the user and ask whether to continue to report generation or investigate.

---

## Phase 3: Report

Delegate to `comparison-report-generator` subagent with:
- The workspace directory path
- The labels for each reference

The subagent reads `comparison-data.json`, annotates the most significant changes with migration-context descriptions, and generates `comparison-report.html`.

---

## Phase 4: Output

Tell the user the path to the generated report and the quality score:

```
Comparison report: $WORK_DIR/comparison-report.html
Quality grade: <grade> (<percent>%)
```

Include the overall quality grade and percentage if scoring was performed.

---

---

## Evaluation Mode

Evaluation mode answers: **How well did an AI migration perform vs the golden truth (SME expert)?** It runs both deterministic pattern detection and adversarial LLM review.

### E1. Collect Inputs

Ask the user for:
- **Golden truth directory**: the expert-produced migration (local path or git URL with branch)
- **Attempts**: one or more named migration attempts to evaluate. Each has a name and a path/URL. Example: `ai-agent=/path/to/ai-output`, `codemods=/path/to/codemods-output`
- **Migration target** (optional): e.g., `patternfly` — enables target-specific pattern detectors and loads default runtime validation config from `targets/<target>_runtime.yaml`
- **Runtime validation**: Ask the user: "Are there runtime validation steps for this migration? How do you verify the app works?" Examples:
  - PatternFly: "run `npm run dev`, screenshot these routes, compare visually"
  - Spring: "run `mvn spring-boot:run`, hit health endpoint, run integration tests"
  - CLI tool: "run these commands, compare output"
  - If a target is specified and a `targets/<target>_runtime.yaml` exists, **offer to use the defaults**: "I found a default runtime config for <target>. Use it, customize it, or skip runtime validation?"

### E2. Deterministic Pipeline

Run the deterministic evaluation pipeline for all attempts against the golden truth:

```bash
python3 scripts/run_evaluation.py \
  --golden <golden_dir> \
  --attempt <name>=<path> \
  [--attempt <name2>=<path2> ...] \
  --output-dir $WORK_DIR \
  [--target <target>]
```

This runs enumerate → diff → categorize → score for each attempt, producing pairwise artifacts in `$WORK_DIR/golden-vs-<name>/`.

**If the script reports errors**, surface them to the user and ask whether to continue.

### E3. Runtime Validation

**If runtime validation is configured** (either from user input or target runtime config):

Delegate to `runtime-validator` subagent with:
- The golden truth directory path
- The list of attempt `(name, path)` pairs
- The validation config (from `targets/<target>_runtime.yaml` or user-provided steps)
- Output directory: `$WORK_DIR`

The subagent validates the golden truth first (baseline), then each attempt, capturing evidence:
- Test results (pass/fail counts, failure messages)
- Screenshots (if Chrome MCP is available and routes are configured)
- Health check responses
- Build/launch errors

**Output**: `$WORK_DIR/runtime-validation.json`

**If runtime validation is not configured**, skip this step. The adversarial agents will still run but without runtime evidence.

### E4. Adversarial Review

Select files for adversarial review: **all files with meaningful diffs** between golden truth and each attempt. Skip identical files and trivial whitespace-only changes.

Load runtime evidence from `$WORK_DIR/runtime-validation.json` if it exists. For each file being reviewed, extract relevant runtime evidence:
- Test failures that reference the file
- Screenshots showing pages that include the file's components
- Build errors mentioning the file

For each attempt, for each selected file, run the three-agent adversarial pipeline in sequence:

1. **Delegate to `bug-finder` subagent** with:
   - The golden truth file content
   - The attempt's file content
   - The unified diff between them
   - The deterministic pattern results for this file
   - Runtime evidence for this file and attempt (test failures, screenshots, errors — if available from runtime validation)
   - Output path: `$WORK_DIR/adversarial/<attempt>/<filename>/bug-finder.json`

2. **Delegate to `adversary` subagent** with:
   - The golden truth file content
   - The attempt's file content
   - The bug-finder's issue list (from step 1)
   - Output path: `$WORK_DIR/adversarial/<attempt>/<filename>/adversary.json`

3. **Delegate to `referee` subagent** with:
   - The golden truth file content (presented as "ground truth")
   - The attempt's file content
   - Each issue with both bug-finder and adversary arguments
   - Runtime evidence for this file and attempt (if available)
   - Output path: `$WORK_DIR/adversarial/<attempt>/<filename>/referee.json`

After all files are processed, consolidate per-file referee results into `$WORK_DIR/llm-assessment.json` with the structure:

```json
{
  "metadata": { "files_assessed": 25 },
  "file_assessments": [
    {
      "attempt": "ai-agent",
      "file": "src/components/AppHeader.tsx",
      "issues": [
        {
          "id": "issue-1",
          "description": "...",
          "severity": "high",
          "impact_score": 10,
          "bug_finder_argument": "...",
          "adversary_argument": "...",
          "referee_verdict": "real",
          "referee_confidence": 0.9
        }
      ],
      "summary_score": 0.6
    }
  ]
}
```

### E5. Compose Results

Run the results composition script:

```bash
python3 scripts/compose_evaluation.py \
  --output-dir $WORK_DIR \
  --golden <golden_dir> \
  --attempt <name>=<path> \
  [--attempt <name2>=<path2> ...] \
  [--target <target>]
```

This produces `$WORK_DIR/evaluation-results.json` with composite scores, cross-attempt comparisons, and problem areas.

### E6. Generate Report

```bash
python3 scripts/generate_evaluation_report.py $WORK_DIR
```

This produces `$WORK_DIR/evaluation-report.html`.

### E7. Output

Tell the user:

```
Evaluation report: $WORK_DIR/evaluation-report.html

Results per attempt:
  <name>: <composite_grade> (<composite_percent>%)
  ...

Problem areas identified: <count>
  [TOP 3 problem areas with severity and description]
```

---

## Guidelines

- **Validate before proceeding** — never silently skip a broken input.
- **Ask the user when something goes wrong** — don't guess or abort without asking.
- **GumTree is optional** — the skill works with text-only diffing. GumTree adds richer AST-level categorization but is not required.
- **Keep the workspace clean** — all outputs go in `$WORK_DIR`.
- **Both layers run by default** — the adversarial LLM review is not optional. The team lacks deep domain expertise, so LLM judges are essential for catching issues detectors miss.
- **All files with meaningful diffs get adversarial review** — skip only identical files and trivial whitespace-only changes.
