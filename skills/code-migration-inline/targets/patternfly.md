# PatternFly Migration

PatternFly 5 to PatternFly 6 migration with visual regression testing.

---

## Pre-Migration

Complete these steps BEFORE starting the fix loop (Phase 2).

### 1. Capture Visual Baseline

Capture screenshots of all important pages before migration begins.

**Steps:**

1. **Discover pages** - Find ALL important pages:
   - Search code for route definitions
   - Look in `pages/`, `views/`, `routes/` folders
   - Check navigation menus and sidebars in code
   - Identify modals, drawers, tabs with distinct content
   - If pages require auth/data, note if you can mock them

2. **Start application and wait** - Run dev server **in the background** (use command from project discovery, append `&` or equivalent). Observe output to find the local URL. Wait for server to respond (poll every second, up to 120 seconds). After server responds, wait additional 5 seconds for JS/assets to load. **Do not proceed until server is ready.**

3. **Capture screenshots** - For each route, use `playwright-mcp`:
   - `browser_navigate` to `<app_url><route>`
   - Wait for page to stabilize
   - `browser_take_screenshot` → save to `$WORK_DIR/baseline/<route-name>.png`

4. **Stop application**

5. **Create manifest** - Create `$WORK_DIR/baseline/manifest.md`:
   ```markdown
   # Visual Baseline
   Captured: <timestamp>

   | Route | Screenshot | Notes |
   |-------|------------|-------|
   | / | home.png | |
   | /dashboard | dashboard.png | |
   ```

**Naming**: `/` → `home.png`, `/dashboard` → `dashboard.png`, `/settings/profile` → `settings-profile.png`

### 2. Run pf-codemods

```bash
npx @patternfly/pf-codemods@latest <project_path> --v6 --fix
```

This auto-fixes many PF5→PF6 issues. Some will still need manual fixes.

### 3. Upgrade Dependencies

```bash
npm install @patternfly/react-core@^6.x @patternfly/react-table@^6.x @patternfly/react-icons@^6.x
npm install
```

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

Complete after E2E tests pass.

### Visual Comparison (Required)

Compare post-migration UI against baseline screenshots.

**Steps:**

1. **Start application and wait** - Run dev server **in the background** (use command from project discovery, append `&` or equivalent). Observe output to find the local URL. Wait for server to respond (poll every second, up to 120 seconds). After server responds, wait additional 5 seconds for JS/assets to load. **Do not proceed until server is ready.**

2. **Capture post-migration screenshots** - For each route in baseline manifest:
   - `browser_navigate` to `<app_url><route>`
   - Wait for page to stabilize
   - `browser_take_screenshot` → save to `$WORK_DIR/post-migration/<route-name>.png`

3. **Stop application**

4. **Compare each page** - **Assume differences exist.** Actively search for problems.

   For each page:
   - Load both images (baseline and post-migration)
   - Describe baseline: list what you see - sections, components, layout
   - Describe post-migration: list what you see in the new screenshot
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

   - List ALL differences found - even small ones
   - Classify: ✓ Identical / ⚠️ Minor (requires fix) / ❌ Major (requires fix)

   **Both minor and major issues require fixes.** Do not mark minor issues as acceptable.

5. **Create report** - Create `$WORK_DIR/visual-diff-report.md` with summary and issues

**Fix ALL issues (major AND minor) before completing migration.** Do not mark minor issues as acceptable.

### Completion Checklist

- [ ] Visual comparison done
- [ ] ALL visual issues fixed (major AND minor)
- [ ] Migration comments removed
