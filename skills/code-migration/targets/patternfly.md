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

Delegate to `visual-baseline` subagent with:
- **work directory**: the `$WORK_DIR` path created in Phase 1 (e.g., `/tmp/migration-02_10_26_14`)
- **output directory**: `$WORK_DIR/baseline`
- **project path**: path to the project source code
- **dev command**: dev server command from project discovery

This creates `$WORK_DIR/manifest.md` and saves screenshots to `$WORK_DIR/baseline/`.

### 2. Run pf-codemods

```bash
npx @patternfly/pf-codemods@latest <project_path> --v6 --fix
```

### 3. Upgrade Dependencies

Check `package.json` for all `@patternfly/*` dependencies and upgrade every one of them to `^6.x`. This includes packages like `@patternfly/react-core`, `@patternfly/react-table`, `@patternfly/react-icons`, `@patternfly/patternfly`, and any others the project uses. Then run `npm install`.

Verify build passes before continuing.

---

## During Migration

**Prefer long-term fixes.** Use new PF6 APIs. Avoid `@ts-ignore`, compatibility wrappers.

Typical order: Import paths → Component APIs → Deprecated patterns → CSS/Styling

---

## Post-Migration

### Visual Regression Loop

Repeat the following loop until no unchecked issues remain. N is the fix round, starting at 0.

**Step 1: Capture screenshots**

Delegate to `visual-baseline` subagent with:
- **work directory**: the `$WORK_DIR` path created in Phase 1 (same path used for baseline)
- **output directory**: `$WORK_DIR/post-migration-N` (N = fix round, starting at 0)
- **project path**: path to the project source code
- **dev command**: dev server command from project discovery

The manifest at `$WORK_DIR/manifest.md` already exists, so it will reuse it and only capture screenshots.

**Step 2: Compare**

Delegate to `visual-compare` subagent with:
- **work directory**: the `$WORK_DIR` path created in Phase 1
- **compare directory**: `$WORK_DIR/post-migration-N`

It compares `$WORK_DIR/baseline/` against the compare directory and creates or updates `$WORK_DIR/visual-diff-report.md`.

**Step 3: Check exit condition**

If all issues in `$WORK_DIR/visual-diff-report.md` are checked (`[x]`) → done, exit loop.

If unchecked (`[ ]`) issues remain → continue to step 4.

**Step 4: Fix**

Delegate to `visual-fix` subagent with:
- **work directory**: the `$WORK_DIR` path created in Phase 1
- **project path**: path to the project source code
- **dev command**: dev server command from project discovery
- **migration context**: a brief 2-3 line summary of the migration so far — include what technologies are involved and what has been done (e.g., codemods applied, which issue groups are fixed, what remains)

It fixes unchecked items, marks them `[x]` in the report, and logs fixes to `$WORK_DIR/visual-fixes.md`.

**Fix ALL issues (major AND minor).** Do not skip any.

Increment N and go back to step 1.

### Completion Checklist

- [ ] Visual comparison done
- [ ] ALL visual issues fixed (all checkboxes in report are `[x]`)
- [ ] Migration comments removed
