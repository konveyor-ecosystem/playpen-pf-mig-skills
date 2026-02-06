---
name: visual-compare
description: Capture post-migration screenshots and compare against baseline. Use in post-migration phase after E2E tests pass.
---

# Visual Comparison

Compare post-migration UI against baseline screenshots.

## Inputs

You receive:
- **Work directory**: must contain `baseline/` folder with manifest
- **Dev command**: command to start the dev server
- **Project path**: path to the project source code

## Prerequisites

Verify baseline exists: `<work_dir>/baseline/manifest.md`

If missing, report error and stop.

## Process

### 1. Read Baseline Manifest

Read `<work_dir>/baseline/manifest.md` to get the list of routes to capture.

### 2. Start Application and Wait

**Run the dev server in the background** and determine the URL from its output:

1. Start the dev server command **in the background** (append `&` or equivalent)
2. Observe the output to find the local URL (e.g., `http://localhost:3000`)
3. Wait for the server to respond (poll every second, up to 120 seconds)
4. After server responds, wait additional 5 seconds for JS/assets to load
5. **Do not proceed until server is ready.** If it doesn't start, report error and stop.

### 3. Capture Post-Migration Screenshots

Create directory: `<work_dir>/post-migration/`

For each route in manifest, use `playwright-mcp`:
1. `browser_navigate` to `<app_url><route>`
2. Wait for page to stabilize
3. `browser_take_screenshot`
4. Save to `<work_dir>/post-migration/<route-name>.png`

Use same naming as baseline.

### 4. Stop Server

Kill the dev server process.

### 5. Compare Each Page

**Assume differences exist.** Actively search for problems.

For each page:

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

5. **List ALL differences found** - even small ones
6. **Classify**:
   - ✓ Identical - no differences
   - ⚠️ Minor - styling changes, spacing, colors (still requires fix)
   - ❌ Major - broken layout, missing elements (requires fix)

**Both minor and major issues require fixes.** Do not mark minor issues as acceptable.

### 6. Create Report

Create `<work_dir>/visual-diff-report.md` with:
- Summary table (counts by status)
- Page-by-page analysis with aspect tables
- Issues to fix list
- Recommendations

## Output

Return the report summary:

```
## Visual Comparison Complete

| Status | Count |
|--------|-------|
| ✓ Identical | N |
| ⚠️ Minor | N |
| ❌ Major | N |

### Issues Found

| Page | Issue | Severity |
|------|-------|----------|
...

Full report: <work_dir>/visual-diff-report.md

**Action Required**: [YES - fix N major and M minor issues / NO - all pages identical]
```
