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

---

## Phase 1: Discovery

### Step 1: Explore Project Structure

Discover build system, test commands, and lint configuration.

**Find build system:**

| File Found | Build Command |
|------------|---------------|
| `package.json` | `npm run build` or `yarn build` |
| `pom.xml` | `mvn compile` or `mvn package` |
| `build.gradle` / `build.gradle.kts` | `./gradlew build` |
| `Makefile` | `make` |
| `go.mod` | `go build ./...` |
| `Cargo.toml` | `cargo build` |
| `*.csproj` / `*.sln` | `dotnet build` |

**Find test commands:**

| Test Type | How to Find |
|-----------|-------------|
| Unit tests | Check `package.json` scripts for `test`, `test:unit`; or `mvn test`, `go test ./...` |
| Integration | Look for `test:integration`, `test:e2e` scripts |
| E2E | Look for Cypress (`cypress run`), Playwright (`npx playwright test`), or similar |

**Find lint command:**

| Tool | Detection |
|------|-----------|
| ESLint | `.eslintrc*` file → `npm run lint` or `npx eslint .` |
| Prettier | `.prettierrc*` file → `npx prettier --check .` |
| Go | `golangci-lint run` |
| Python | `flake8`, `pylint`, `ruff` |

**Record findings:**

```
Build: <command>
Lint: <command>
Unit tests: <command>
Integration tests: <command>
E2E tests: <command>
Primary language: <language>
```

### Step 2: Build Kantra Command

Construct the Kantra analyze command flags.

**Ask user:**
- Use custom rules? (If yes, get path)
- Enable default rulesets?

**Detect provider:**

| Files Found | Provider |
|-------------|----------|
| `*.java`, `pom.xml`, `build.gradle` | `java` |
| `*.ts`, `*.tsx`, `package.json` with TS deps | `typescript` |
| `*.js`, `*.jsx`, `package.json` | `javascript` |
| `go.mod`, `*.go` | `go` |
| `*.py`, `requirements.txt`, `pyproject.toml` | `python` |
| `*.cs`, `*.csproj` | `dotnet` |

**Build flags:**

```bash
# Base flags
--provider=<detected_provider>

# If custom rules provided:
--rules=<path_to_rules>

# If default rulesets enabled (and available for target):
--target=<migration_target>
```

**You add `--input` and `--output`:**

```bash
kantra analyze --input <project> --output $WORK_DIR/round-N/kantra <FLAGS>
```

### Step 3: Create Workspace

```bash
WORK_DIR=$(mktemp -d -t migration-XXXXXX)
```

### Step 4: Check Target Technology Specific Guidance

Read `targets/<target>.md` if it exists. Follow pre-migration steps before Phase 2.

---

## Phase 2: Fix Loop

### First Round Only

Run initial analysis to create the fix plan:

1. Run Kantra: `kantra analyze --input <project> --output $WORK_DIR/round-1/kantra <FLAGS>`
2. Run build and lint commands
3. Run unit tests
4. Collect ALL issues from ALL sources (see Issue Sources table)
5. Create `$WORK_DIR/status.md` using the template below

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
3. **Validate**: Run Kantra, build, lint, unit tests
4. **Update**: Mark group done, log the round

**Run tests concisely:**
- Capture output, report only failures
- Format: `PASS: X tests, FAIL: Y tests`
- For failures, show test name and error message only

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

### If Stuck (Same Issue 3+ Rounds)

When an issue persists across 3+ rounds, analyze it:

**Run persistent issues script:**
```bash
python scripts/persistent_issues_analyzer.py $WORK_DIR
```

**For each persistent issue, determine:**

| Question | Check |
|----------|-------|
| False positive? | Rule too strict? Pattern actually valid? |
| Fixable? | Multiple approaches failed? Needs manual decision? |
| Blocking factor? | External deps? Domain knowledge needed? |

**Categorize:**
- **Fix**: Real issue, try different approach
- **Ignore**: False positive, document why in status.md
- **Document**: Real but needs manual intervention, add to status.md

---

## Phase 3: Final Validation

Run E2E/behavioral tests and complete target-specific validation.

### E2E Testing

1. Run E2E test command discovered in Phase 1
2. Report results concisely (pass/fail counts, failure details)
3. If tests FAIL → Fix issues, re-run
4. If tests PASS → Continue to target validation

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
- **Report test results concisely** - counts and failures only, not full output
