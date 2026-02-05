# Visual Testing Guide

Detailed instructions for capturing and comparing screenshots during UI migrations.

---

## Capturing Screenshots

### Discover Routes

```bash
grep -rE "(path=|path:)" --include="*.tsx" --include="*.jsx" --include="*.ts" --include="*.js" <project_path>/src
```

Look for:
- `<Route path="/dashboard" ...>`
- `{ path: "/settings", element: ... }`
- `createBrowserRouter([{ path: "/" ... }])`

Additionally, look at the source code to identify important components, pages in the application.

### Run application & wait for it to be ready

```bash
cd <project_path>
<dev_command> &
DEV_PID=$!

# Wait for server ready
for i in {1..60}; do
  curl -s http://localhost:3000 > /dev/null && break
  sleep 1
done
```

### Capture Each Route

Using playwright-mcp (must be configured):

1. `browser_navigate` to `http://localhost:3000<route>`
2. Wait for page to stabilize (network idle)
3. `browser_take_screenshot`
4. Save to appropriate directory

**Naming convention:**
- `/` → `home.png`
- `/dashboard` → `dashboard.png`
- `/settings/profile` → `settings-profile.png`

### Stop Server and Create Manifest

```bash
kill $DEV_PID
```

Create manifest file:

```markdown
# Visual Baseline

Captured: <timestamp>
Project: <project_path>

## Pages

| Route | Screenshot |
|-------|------------|
| / | home.png |
| /dashboard | dashboard.png |
| /settings | settings.png |
```

---

## Comparing Screenshots

### Post-Migration Capture

1. Start dev server (same as baseline)
2. Navigate to each route from manifest
3. Capture screenshots → `$WORK_DIR/post-migration/<route>.png`
4. Stop dev server

### Analysis

For each page, compare baseline vs post-migration:

1. Load both images
2. Analyze for:
   - **Layout**: Element positions, spacing, alignment
   - **Styling**: Backgrounds, borders, colors
   - **Missing elements**: Components that disappeared
   - **New elements**: Unexpected additions
   - **Typography**: Font size, weight, line height

### Classification

| Status | Meaning | Action |
|--------|---------|--------|
| ✓ No change | Identical | None |
| ⚠️ Minor | Small styling tweaks | Review if expected |
| ❌ Major | Layout broken, elements missing | Fix before completing |

---

## Visual Diff Report

Create `$WORK_DIR/visual-diff-report.md`:

```markdown
# Visual Comparison Report

Compared: <timestamp>
Baseline: $WORK_DIR/baseline
Post-migration: $WORK_DIR/post-migration

## Summary

| Status | Count |
|--------|-------|
| ✓ No change | N |
| ⚠️ Minor differences | N |
| ❌ Major regressions | N |

## Page-by-Page Analysis

### / (Home)
**Status**: ✓ No change
**Notes**: Page appears identical to baseline.

### /dashboard
**Status**: ⚠️ Minor differences
**Changes**:
- Card spacing increased (expected PF6 change)
- Button border radius updated

**Assessment**: Acceptable PF6 styling updates.

### /settings
**Status**: ❌ Major regression
**Changes**:
- Navigation sidebar missing
- Form layout broken

**Assessment**: Requires fix. Likely CSS class changes not migrated.

## Recommendations

1. Fix major regressions before completing
2. Review minor differences for PF6 alignment
3. Document intentional visual changes
```
