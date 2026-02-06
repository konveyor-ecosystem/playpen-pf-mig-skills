# PatternFly Migration

PatternFly 5 to PatternFly 6 migration with visual regression testing.

---

## Pre-Migration

Complete these steps BEFORE starting the fix loop (Phase 2).

### 1. Capture Visual Baseline

Delegate to `visual-baseline` sub-agent with:
- `work_dir`: `$WORK_DIR`
- `project_path`: path to the project
- `dev_command`: dev server command (from project discovery)

The sub-agent will start the application, wait for it to be ready, capture screenshots, then stop it.

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

Delegate to `visual-compare` sub-agent with:
- `work_dir`: `$WORK_DIR`
- `project_path`: path to the project
- `dev_command`: dev server command (from project discovery)

The sub-agent will start the application, wait for it to be ready, capture screenshots, compare against baseline, then stop it.

**Fix ALL issues (major AND minor) before completing migration.** Do not mark minor issues as acceptable.

### Completion Checklist

- [ ] Visual comparison done
- [ ] ALL visual issues fixed (major AND minor)
- [ ] Migration comments removed

