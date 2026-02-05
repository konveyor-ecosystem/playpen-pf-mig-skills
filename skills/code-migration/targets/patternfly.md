# PatternFly Migration

PatternFly 5 to PatternFly 6 migration with visual regression testing.

---

## Pre-Migration

Complete these steps BEFORE starting the fix loop (Phase 2).

### 1. Capture Visual Baseline

Take screenshots of all routes before making changes. This enables visual regression detection.

**Steps:**
1. Find important routes / pages / components in the application
   - If routes require authorization, mock data, understand whether you can mock them
2. Run the application (preferably in dev mode) in background
3. For each route, use `playwright-mcp`:
   - `browser_navigate` to route
   - `browser_take_screenshot` → save to `$WORK_DIR/baseline/<route>.png`
4. Stop application
5. Create `$WORK_DIR/baseline/manifest.md` listing all captured pages

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

1. Capture post-migration screenshots (same routes as baseline)
2. Compare each page against baseline
3. Classify differences in each page:
   - **⚠️ Minor**
      - Expected PF6 styling updates
      - Theme / color changes
      - Padding issues
   - **❌ Major**: Broken layout, missing elements
   - If no issues found, mark the page as identical.
4. Fix major & minor regressions before completing migration

For detailed visual testing steps, see [visual-testing.md](visual-testing.md).

### Completion Checklist

- [ ] Visual comparison done
- [ ] Major regressions fixed
- [ ] Migration comments removed

