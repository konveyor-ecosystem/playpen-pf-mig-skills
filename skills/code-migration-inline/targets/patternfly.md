# PatternFly Migration

PatternFly 5 to PatternFly 6 migration with visual regression testing.

## Workflow

```
Pre-Migration → Phase 2 (Fix Loop) → Phase 3 (E2E Tests) → Visual Comparison → Visual Fix → Done
```

---

## Pre-Migration

Complete BEFORE Phase 2.

### 1. Capture Visual Baseline

Discover all UI components and capture baseline screenshots.

**Steps:**

1. **Discover all UI elements** - Find ALL important elements (not just routes):

   **Routes/Pages:**
   - Search for router config, route arrays, path definitions
   - Check `pages/`, `views/`, `routes/`, `screens/` folders
   - Find menus, sidebars, navbars and extract all links

   **Interactive Components:**
   - Modals/Dialogs and their triggers
   - Drawers/Sidepanels
   - Forms in modals or triggered by actions
   - Tabs, accordions, dropdowns with distinct content

   **Do not skip any discoverable element.** For each element, note what triggers it and any required state/data.

2. **Create manifest** - Create `$WORK_DIR/manifest.md`:
   ```markdown
   # UI Manifest
   Project: <project_path>

   ## Routes
   | Route | Screenshot | Notes |
   |-------|------------|-------|
   | / | home.png | |
   | /dashboard | dashboard.png | |

   ## Interactive Components
   | Type | Name | Screenshot | Trigger |
   |------|------|------------|---------|
   | Modal | Confirm Delete | modal-confirm-delete.png | Click delete button |
   | Drawer | Settings | drawer-settings.png | Click gear icon |
   ```

3. **Start application and wait** - Run dev server **in the background** (use command from project discovery, append `&` or equivalent). Observe output to find the local URL. Wait for server to respond (poll every second, up to 120 seconds). After server responds, wait additional 5 seconds for JS/assets to load. **Do not proceed until server is ready.**

4. **Capture screenshots** - For each element in manifest, use `playwright-mcp`:
   - Navigate to page or trigger component
   - Wait for content to stabilize
   - Take screenshot → save to `$WORK_DIR/baseline/<name>.png`

5. **Stop application**

**Naming**: `/` → `home.png`, `/dashboard` → `dashboard.png`. Components: `modal-<name>.png`, `drawer-<name>.png`, `form-<name>.png`

### 2. Run pf-codemods

```bash
npx @patternfly/pf-codemods@latest <project_path> --v6 --fix
```

This auto-fixes many PF5→PF6 issues. Some will still need manual fixes.

### 3. Upgrade Dependencies

Check `package.json` for all `@patternfly/*` dependencies and upgrade every one of them to `^6.x`. This includes packages like `@patternfly/react-core`, `@patternfly/react-table`, `@patternfly/react-icons`, `@patternfly/patternfly`, and any others the project uses. Then run `npm install`.

Verify build passes after upgrade. Address any obvious issues with the build before moving forward.

---

## During Migration

### Fix Strategy

**Prefer long-term fixes over workarounds.**

Do:

- Use new PF6 APIs and components
- Refactor to match PF6 patterns
- Remove compatibility layers

Avoid:
- Suppressing warnings without fixing
- Using `// @ts-ignore` on deprecated props
- Creating wrappers that preserve old APIs

### Typical Group Order

Adapt based on your findings:

1. **Import paths** - Fix module imports first
2. **Component API changes** - Removed/renamed props
3. **Deprecated API replacements** - Old patterns → new
4. **CSS/Styling** - Class names, design tokens

---

## Post-Migration

### Visual Regression Loop

Repeat the following loop until no unchecked issues remain. N is the fix round, starting at 0.

**Step 1: Capture screenshots**

Read `$WORK_DIR/manifest.md` (already created during pre-migration).

1. **Start application and wait** - Run dev server **in the background**. Wait for server to respond. **Do not proceed until server is ready.**
2. **Capture screenshots** - For each element in manifest, use `playwright-mcp`:
   - Navigate to page or trigger component
   - Wait for content to stabilize
   - Take screenshot → save to `$WORK_DIR/post-migration-N/<name>.png` (N = fix round, starting at 0)
3. **Stop application**

**Step 2: Compare**

Compare `$WORK_DIR/baseline/` against `$WORK_DIR/post-migration-N/`.

**Assume differences exist.** Actively search for problems.

For each element in manifest:
- Load both images (baseline and post-migration)
- Describe what you see in each
- Compare each aspect:

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

- List ALL differences found - even small ones
- Classify: ✓ Identical / ⚠️ Minor (requires fix) / ❌ Major (requires fix)

**Both minor and major issues require fixes.** Do not mark minor issues as acceptable.

**Create or update report** - Write `$WORK_DIR/visual-diff-report.md` with checkbox-tracked issues:

```markdown
# Visual Comparison Report

## Issues

### /dashboard
- [ ] Card spacing increased ~4px (⚠️ Minor)
- [ ] Button borders slightly darker (⚠️ Minor)

### /settings
- [ ] Navigation sidebar missing (❌ Major)
```

If the report already exists: mark fixed issues as `[x]`, add new issues as `[ ]`.

**Step 3: Check exit condition**

If all issues in `$WORK_DIR/visual-diff-report.md` are checked (`[x]`) → done, exit loop.

If unchecked (`[ ]`) issues remain → continue to step 4.

**Step 4: Fix**

Read `$WORK_DIR/status.md` to understand what migration issues have been fixed so far. This helps identify root causes of visual regressions.

Fix unchecked issues by page/route:

1. **Group unchecked issues by page**
2. **For each page with unchecked issues**:
   - Analyze baseline and post-migration screenshots
   - Identify cause in code (CSS changes, component API changes, etc.)
   - Make code changes to resolve
   - Verify:
     - Start app **in the background** (append `&` or equivalent)
     - Wait for server to be ready
     - Use `playwright-mcp` to navigate to the page, take new screenshot
     - Compare against baseline
     - Stop the app
   - Iterate until fixed
   - Mark fixed issues as `[x]` in `$WORK_DIR/visual-diff-report.md`
   - Append a brief (2-3 line) summary to `$WORK_DIR/visual-fixes.md` describing what was changed and why. Do not wait until all pages are done.

**Fix ALL issues (major AND minor) before completing migration.** Do not mark minor issues as acceptable.

Increment N and go back to step 1.

### Completion Checklist

- [ ] Visual comparison done
- [ ] ALL visual issues fixed (all checkboxes in report are `[x]`)
- [ ] Migration comments removed
