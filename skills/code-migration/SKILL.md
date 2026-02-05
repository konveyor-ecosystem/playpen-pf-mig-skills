---
name: code-migration
description: Migrate applications between technologies using kantra static analysis and automated fixes. Use when migrating Java, Node.js, Python, Go, or .NET applications. Keywords: kantra, migration, upgrade, modernize.
---

# Code Migration

Migrate applications by identifying issues from multiple sources, fixing them systematically, and validating the result.

## Issue Sources

Collect issues from ALL of these sources during analysis.

| Source | Examples |
|--------|----------|
| Kantra analysis | Deprecated APIs, breaking changes, migration patterns |
| Build errors | Compilation failures, type errors, missing deps |
| Lint errors | Style violations, unused imports |
| Test failures | Broken tests from API changes |
| Target docs | Breaking changes Kantra doesn't detect (check `targets/<target>.md`) |

Kantra is a static source code analysis tool that uses rules to identify migration issues in the source code.

## Sub-Agents

Delegate to these specialized agents:

| Task | Sub-Agent | When |
|------|-----------|------|
| Discover project structure | `project-explorer` | Start of Phase 1 |
| Build Kantra command | `kantra-command-builder` | Phase 1, after discovery |
| Run tests | `test-runner` | Every validation step |
| Analyze stuck issues | `issue-analyzer` | Same issue appears 3+ rounds |

---

## Phase 1: Discovery

1. **Explore project**: Delegate to `project-explorer`. Get build command, test commands, lint command.

2. **Build Kantra command**: Ask user:
   - Use custom rules? (If yes, get path)
   - Enable default rulesets?

   Delegate to `kantra-command-builder` with user's answers. It returns flags; you add `--input` and `--output`.

3. **Create workspace**: Create temp directory *outside* the project:
   ```bash
   WORK_DIR=$(mktemp -d -t migration-XXXXXX)
   ```

4. **Check target technology specific guidance**: Read `targets/<target>.md` if it exists. Follow pre-migration steps before Phase 2.

---

## Phase 2: Fix Loop

### First Round Only

Run initial analysis to create the fix plan:

1. Run Kantra: `kantra analyze --input <project> --output $WORK_DIR/round-1/kantra <FLAGS>`
2. Run build, lint, unit tests (delegate to `test-runner` for tests)
3. Collect ALL issues from ALL sources (see Issue Sources table)
4. Create `$WORK_DIR/status.md` using the template below

### Fix Loop Template

Create `$WORK_DIR/status.md`:

```markdown
# Migration Status

## Groups

- [ ] Group 1: [Name] - [Brief description]
- [ ] Group 2: [Name] - [Brief description]
- [ ] Group 3: [Name] - [Brief description]

## Group Details

### Group 1: [Name]
**Why grouped**: [Related issues, same subsystem, etc.]
**Issues**:
- [Issue from Kantra/build/lint/tests]
- [Issue from Kantra/build/lint/tests]
**Files**: [file1.ts, file2.ts]

### Group 2: [Name]
...

## Round Log

(Append after each round)
```

### Each Round

```
Round Checklist:
- [ ] Pick next incomplete group
- [ ] Apply fixes for that group
- [ ] Run Kantra + build + lint + unit tests
- [ ] Mark group complete in status.md
- [ ] Add new issues to plan if any appeared
```

1. **Pick**: Select first incomplete group from status.md
2. **Fix**: Apply all fixes for that group
3. **Validate**: Run Kantra, build, lint, unit tests (delegate tests to `test-runner`)
4. **Update**: Mark group done, log the round

Append to status.md:
```markdown
### Round N: [Group Name]
- Fixed: [count] issues
- New issues: [count or "none"]
- Build: PASS/FAIL
- Tests: PASS/FAIL/NONE
```

### Exit Check

After each round, check:

| Condition | Done? |
|-----------|-------|
| All groups complete | ☐ |
| Kantra: 0 issues | ☐ |
| Build: passes | ☐ |
| Unit tests: pass | ☐ |

- **Any unchecked** → Continue loop (next group)
- **All checked** → Proceed to Phase 3

### If Stuck

If the same issue appears 3+ rounds, delegate to `issue-analyzer` to determine if it's fixable, a false positive, or needs manual attention.

---

## Phase 3: Final Validation

Run E2E/behavioral tests and complete target-specific validation.

### E2E Testing

1. Delegate to `test-runner` with E2E test commands
2. If tests FAIL → Fix issues, re-run
3. If tests PASS → Continue to target validation

### Target Validation

Check `targets/<target>.md` for post-migration steps (e.g., visual comparison for UI migrations).

### Exit Criteria

All must be checked:

- [ ] Kantra: 0 issues
- [ ] Build: passes
- [ ] Unit tests: pass
- [ ] E2E tests: pass
- [ ] Target-specific validation complete

Update status.md:
```markdown
## Complete

- Total rounds: N
- Build: PASS
- Unit tests: PASS
- E2E tests: PASS
- Target validation: PASS
```

---

## Guidelines

- **One group per round** for clear feedback
- **Follow planned order** - foundation before dependent changes
- **Verify each fix** - don't break existing features
- **Document unfixable issues** after 2+ failed approaches
- **Use all issue sources** - Kantra is just one input
