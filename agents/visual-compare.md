---
name: visual-compare
description: Compare screenshots between baseline and post-migration directories. Generates or updates a checkbox-tracked report.

# For Gemini CLI, uncomment the tools section below:
# tools:
#   - run_shell_command
#   - list_directory
#   - read_file
#   - write_file
#   - search_file_content
#   - replace
#   - glob
# For Claude Code, tools may be inherited from global settings
# tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

# Visual Comparison

Compare screenshots between baseline and post-migration directories. Generate or update a checkbox-tracked report.

## Inputs

- **Work directory**: workspace root (contains `baseline/`, `manifest.md`, and `visual-diff-report.md`)
- **Compare directory**: directory with post-migration screenshots to compare against baseline

## Prerequisites

Verify these exist before proceeding:
- `<work_dir>/manifest.md`
- `<work_dir>/baseline/` with screenshots

If either is missing, report error and stop.

## Process

### 1. Read Manifest

Read `<work_dir>/manifest.md` to get the list of elements to compare.

### 2. Compare Each Element

For each element in the manifest, load the screenshot from `<work_dir>/baseline/` and `<compare_dir>/`.

**Assume differences exist.** Actively search for problems.

For each element:

1. **Load both images**: baseline and post-migration
2. **Describe baseline**: List what you see - sections, components, layout
3. **Describe post-migration**: List what you see in the new screenshot
4. **Compare each aspect** - for EACH, state what you found:

   | Aspect | Check | Your Finding |
   |--------|-------|--------------|
   | Layout | Sections same position/size? | [state: same OR describe difference] |
   | Navigation | Sidebar/header/links present? | [state: same OR describe difference] |
   | Components | All buttons/forms/tables/cards present? | [state: same OR describe difference] |
   | Text | Labels readable? No truncation? | [state: same OR describe difference] |
   | Spacing | Consistent gaps? No overlaps? | [state: same OR describe difference] |
   | Colors | Background/text/borders correct? | [state: same OR describe difference] |
   | Icons | All visible and sized correctly? | [state: same OR describe difference] |

**You MUST fill in the "Your Finding" column for EVERY row.** Do not skip any aspect.

5. **List ALL differences found** - even small ones
6. **Classify**:
   - ✓ Identical - no differences found in any aspect
   - ⚠️ Minor - styling changes, spacing, colors (still requires fix)
   - ❌ Major - broken layout, missing elements (requires fix)

**Both minor and major issues require fixes.** Do not mark minor issues as acceptable.

### 3. Write Report

Create or update `<work_dir>/visual-diff-report.md`.

**If the report does NOT exist**, create it with all issues as unchecked:

```markdown
# Visual Comparison Report

Compared: <timestamp>
Baseline: <work_dir>/baseline
Post-migration: <compare_dir>

## Issues

### /dashboard
- [ ] Card spacing increased ~4px (⚠️ Minor)
- [ ] Button borders slightly darker (⚠️ Minor)

### /settings
- [ ] Navigation sidebar missing (❌ Major)
- [ ] Form layout broken - fields overlap (❌ Major)
- [ ] Submit button not visible (❌ Major)
```

**If the report already exists**, update it:
1. For each previously reported issue: if now fixed (screenshots match), change `[ ]` to `[x]`
2. For any new issues found: append as `[ ]` under the appropriate page heading

Pages with no issues should NOT appear in the report.

## Output

Return the report summary:

```
## Visual Comparison Complete

| Status | Count |
|--------|-------|
| ✓ No issues | N |
| ⚠️ Minor | N |
| ❌ Major | N |
| ✅ Previously fixed | N |

Unchecked issues remaining: N

Report: <work_dir>/visual-diff-report.md

**Action Required**: [YES - N unchecked issues remain / NO - all resolved]
```
