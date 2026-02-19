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

   **Authentication:** Check whether the application requires login. Look for login pages, auth guards, hardcoded credentials in seed files, `.env.example`, test fixtures, or README instructions. Record any credentials needed to access protected routes so they can be used during screenshot capture.

   **Do not skip any discoverable element.** For each element, note what triggers it and any required state/data.

2. **Create manifest** - Create `$WORK_DIR/manifest.md`. Each entry must describe exactly what to capture and how to reach the target state:
   ```markdown
   # UI Manifest
   Project: <project_path>

   ## Routes

   ### / → home.png
   - **Navigate to**: root URL (`/`)
   - **Wait for**: page content to fully render (stats, tables, lists)
   - **Key elements**: sidebar navigation, stats cards row, data table with action buttons

   ### /dashboard → dashboard.png
   - **Navigate to**: `/dashboard`
   - **Wait for**: all dashboard widgets to load
   - **Key elements**: chart area, summary cards, recent activity list

   ## Interactive Components

   ### Modal: Confirm Delete → modal-confirm-delete.png
   - **Trigger**: on `/dashboard`, click the delete button on any table row
   - **Wait for**: modal to appear and content to render
   - **Key elements**: modal title, confirmation message, Cancel and Confirm buttons

   ### Drawer: Settings → drawer-settings.png
   - **Trigger**: click the gear icon in the top navigation
   - **Wait for**: drawer panel to slide in and content to load
   - **Key elements**: settings form fields, save/cancel buttons
   ```

3. **Start application and wait** - **The application MUST be running and fully responsive before any `playwright-mcp` interaction.** Playwright operations will fail if the server is not ready. Run dev server **in the background** (append `&` or equivalent) and capture the process ID. Extract the local URL from the server output. **Poll the URL every 2 seconds, up to 120 seconds**, until it returns a successful response. **After the server responds, wait an additional 5 seconds** for JS bundles and assets to fully load. **Do not call any `playwright-mcp` tool until both checks pass.**

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

**Visual regression testing is required.** Do not skip the visual comparison loop. The migration is incomplete until all visual issues are resolved and every checkbox in the report is checked.

### Visual Regression Loop

Repeat the following loop until no unchecked issues remain. N is the fix round, starting at 0.

**Step 1: Capture screenshots**

Read `$WORK_DIR/manifest.md` (already created during pre-migration).

1. **Start application and wait** - **The application MUST be running and fully responsive before any `playwright-mcp` interaction.** Run dev server **in the background** (append `&`) and capture the process ID. **Poll the URL every 2 seconds, up to 120 seconds.** After the server responds, **wait an additional 5 seconds** for JS bundles and assets. **Do not call any `playwright-mcp` tool until both checks pass.**
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
     **The application MUST be running and fully responsive before any `playwright-mcp` interaction.**
     - Start app **in the background** (append `&`) and capture the process ID
     - **Poll the URL every 2 seconds, up to 120 seconds.** After the server responds, **wait an additional 5 seconds** for JS bundles and assets. **Do not call any `playwright-mcp` tool until both checks pass.**
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
