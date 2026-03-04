# Skill: Migration Comparison

A [Claude Code skill](https://code.claude.com/docs/en/skills) (also compatible with [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)) that compares two migration attempts of the same codebase using AST diffing ([GumTree](https://github.com/GumTreeDiff/gumtree)) with text diff fallback. Produces a self-contained HTML comparison report with categorized changes, semantic analysis, and side-by-side diffs. This skill delegates specialized tasks to [subagents](https://code.claude.com/docs/en/sub-agents).

## Prerequisites

- [Claude Code](https://code.claude.com/) or [Gemini CLI](https://geminicli.com/)
- Python 3 (for helper scripts)
- **Optional**: [GumTree](https://github.com/GumTreeDiff/gumtree) for AST-level diffing. Without it, the skill uses text-only diffing (still produces a useful report). Install via:
  - `podman pull gumtreediff/gumtree` or `docker pull gumtreediff/gumtree` (container)
  - Or download the native binary from [GitHub releases](https://github.com/GumTreeDiff/gumtree/releases)

## Setup

### Claude Code

1. Copy `skills/migration-comparison/` (including `scripts/` and `targets/`) to `.claude/skills/migration-comparison/` in your project (or `~/.claude/skills/migration-comparison/` for global availability).
2. Copy the required agents to `.claude/agents/` in your project (or `~/.claude/agents/`):
   - `agents/repo-differ.md`
   - `agents/comparison-report-generator.md`
3. The skill is auto-discovered by Claude Code when relevant to your conversation. Restart your session after adding new agent files.

See [Claude Code skills docs](https://code.claude.com/docs/en/skills) for more on skill placement and discovery.

### Gemini CLI

1. Copy `skills/migration-comparison/` to `.gemini/skills/migration-comparison/` in your workspace (or `~/.gemini/skills/migration-comparison/`).
2. Copy the required agents to `.gemini/agents/`:
   - `agents/repo-differ.md`
   - `agents/comparison-report-generator.md`
3. **Uncomment the `tools:` section** in each agent `.md` file. Gemini CLI requires explicit tool declarations in the YAML frontmatter.
4. Enable experimental agents in your Gemini CLI settings:
   ```json
   {
     "experimental": {
       "enableAgents": true
     }
   }
   ```

## Subagents

| Subagent | Description |
|----------|-------------|
| `repo-differ` | Runs the diff pipeline: file enumeration, AST/text diffing, change categorization |
| `comparison-report-generator` | Annotates significant changes and generates the HTML comparison report |

## Usage

Start a session in any directory and ask Claude to compare two migration attempts:

```
Compare the migration in /path/to/agent-output against /path/to/ground-truth
```

The skill will ask you for:
- **Reference A** and **Reference B**: local directory paths or git URLs with branches (e.g., `https://github.com/org/repo@branch`)
- **Labels** for each reference (e.g., "Ground Truth", "Agent A")
- **File filters** (optional): glob patterns to restrict comparison (e.g., `*.tsx`, `src/**/*.ts`)

The output is a self-contained HTML report at `$WORK_DIR/comparison-report.html`.

## Running Scripts Directly

You can also run the pipeline manually without the skill:

```bash
# 1. Enumerate files and build manifest
python3 scripts/enumerate_files.py /path/to/dir_a /path/to/dir_b \
  --label-a "Ground Truth" --label-b "Agent A" \
  --output-dir /tmp/workspace

# 2. Run diffs (uses GumTree if available, text diff fallback)
python3 scripts/run_diffs.py \
  --manifest /tmp/workspace/file-manifest.json \
  --dir-a /path/to/dir_a --dir-b /path/to/dir_b \
  --output-dir /tmp/workspace

# 3. Categorize changes
python3 scripts/categorize_changes.py \
  --manifest /tmp/workspace/file-manifest.json \
  --diff-results /tmp/workspace/diff-results.json \
  --dir-a /path/to/dir_a --dir-b /path/to/dir_b \
  --label-a "Ground Truth" --label-b "Agent A" \
  --output-dir /tmp/workspace

# 4. Score migration quality (optional: add --target patternfly for PF-specific patterns)
python3 scripts/score_migration.py \
  --comparison-data /tmp/workspace/comparison-data.json \
  --dir-a /path/to/dir_a --dir-b /path/to/dir_b \
  --output-dir /tmp/workspace \
  --target patternfly

# 5. Generate HTML report (automatically includes scoring if scoring-results.json exists)
python3 scripts/generate_comparison_report.py /tmp/workspace
```

### Useful flags

- `python3 scripts/run_diffs.py --check-gumtree` — check GumTree availability without running diffs
- `python3 scripts/run_diffs.py --no-gumtree ...` — skip GumTree, use text diff only
- `python3 scripts/enumerate_files.py dir_a dir_b --check-only` — report overlap stats without building full manifest
- `python3 scripts/enumerate_files.py dir_a dir_b --filter '*.tsx'` — restrict to specific file patterns

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `scripts/enumerate_files.py` | Walks two directory trees, computes SHA-256 hashes, classifies files as added/removed/modified/identical |
| `scripts/run_diffs.py` | Executes GumTree AST diffs (native/podman/docker) with text diff fallback, parallel execution |
| `scripts/categorize_changes.py` | Assigns change categories: structural, semantic, API changes, cosmetic, additive, subtractive |
| `scripts/score_migration.py` | Scores migration quality: file coverage, pattern detection, noise analysis |
| `scripts/generate_comparison_report.py` | Generates a self-contained HTML report from `comparison-data.json` |

## GumTree Support

GumTree provides AST-level diffing for richer change categorization. The skill probes for it in order: native binary, podman, docker.

**Supported file extensions** (based on GumTree's bundled generators):

`.ts`, `.js`, `.py`, `.java`, `.css`, `.go`, `.rs`, `.rb`, `.c`, `.cpp`, `.h`, `.hpp`, `.kt`, `.swift`, `.php`, `.ml`, `.yaml`, `.yml`, `.xml`

**Not supported**: `.tsx`, `.jsx` — these fall back to text diffing automatically.

## Migration Quality Scoring

The pipeline includes a quality scoring step that evaluates migration candidates against a reference. The score is computed from three weighted components:

- **File Coverage (20%)**: proportion of reference files present in the candidate
- **Pattern Score (65%)**: weighted accuracy of migration pattern application (target-specific when `--target` is used, heuristic-based otherwise)
- **Noise Penalty (15%)**: deductions for debug artifacts, placeholder tokens, formatting-only changes, and unnecessary modifications

Grade scale: A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, F < 60.

When a `--target` is specified, the scorer loads pattern detectors from `targets/<target>_patterns.py`. These detectors use tree-sitter AST analysis (for TSX/TS files) and regex on diff text to check whether specific migration patterns were correctly applied.

### Available Targets

| Target | Description | Patterns |
|--------|-------------|----------|
| `patternfly` | PatternFly 5 → 6 migration | 24 patterns (12 trivial, 9 moderate, 3 complex) |

### Tree-sitter Dependencies

The scoring step requires `tree-sitter` and `tree-sitter-typescript` for AST analysis. Install them via:

```bash
pip install tree-sitter>=0.23 tree-sitter-typescript>=0.23
```

Or use the provided wrapper script (`scripts/run_pipeline.sh`) which automatically sets up a virtual environment with the required dependencies.

## Known Limitations

- GumTree's Docker image does not include generators for `.tsx`/`.jsx` files; these use text diff
- GumTree may exit 0 on unsupported files with no output; the scripts detect this and fall back to text diff
- AST diffing is skipped for files larger than 1MB
- Side-by-side view in the HTML report truncates diffs longer than 200 lines
- Subagents run in isolation and do not share conversation history with the main agent
