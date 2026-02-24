# Migration Status: PatternFly 5 → PatternFly 6

## Groups

- [x] Group 1: Deprecated Select Components - Rewrite SelectFilterControl and MultiselectFilterControl
- [x] Group 2: OptionPropsWithKey Type Updates - Fix type definitions for filter options
- [x] Group 3: Pagination API Rename - alignRight → alignEnd
- [x] Group 4: CSS Class Prefix Updates - pf-v5 → pf-v6 across all source files
- [x] Group 5: Test Fixes - Update snapshots, class selectors, and toolbar interaction tests
- [x] Group 6: ESLint False Positive Suppression - Add disable comments for import/named

## Group Details

### Group 1: Deprecated Select Components
**Why grouped**: PF6 removed Select/SelectOption/SelectVariant from deprecated exports
**Issues**:
- SelectFilterControl.tsx: Rewrote to use PF6 composable Select + MenuToggle + SelectList + SelectOption
- MultiselectFilterControl.tsx: Rewrote to use PF6 composable Select with checkbox variant + TextInputGroup for filtering
- FilterToolbar.tsx: Removed deprecated SelectOptionProps import
**Files**: SelectFilterControl.tsx, MultiselectFilterControl.tsx, FilterToolbar.tsx

### Group 2: OptionPropsWithKey Type Updates
**Why grouped**: Type interface changed when Select was replaced
**Issues**:
- OptionPropsWithKey: Redefined with own properties (key, value, label, children, isDisabled) instead of extending SelectOptionProps
- viewCredentialsList.tsx: label property now valid on OptionPropsWithKey
- viewSourcesList.tsx: label property now valid on OptionPropsWithKey
**Files**: FilterToolbar.tsx, viewCredentialsList.tsx, viewSourcesList.tsx

### Group 3: Pagination API Rename
**Why grouped**: Simple API rename
**Issues**:
- usePaginationPropHelpers.ts: Changed 'alignRight' to 'alignEnd'
**Files**: usePaginationPropHelpers.ts

### Group 4: CSS Class Prefix Updates
**Why grouped**: All pf-v5 CSS class references need updating to pf-v6
**Issues**:
- viewLayoutToolbar.tsx: pf-v5-theme-dark → pf-v6-theme-dark (add and remove)
- viewLayoutToolbar.tsx: pf-v5-c-avatar → pf-v6-c-avatar
- showSourceConnectionsModal.css: pf-v5-c-table → pf-v6-c-table variable override
- select-overrides.css: pf-v5-c-select → pf-v6-c-select scrollable override
- showAggregateReportModal.tsx: pf-v5-u-mb-lg → pf-v6-u-mb-lg
- viewLayoutToolbar.css: No changes needed (no pf-v5 refs)
**Files**: viewLayoutToolbar.tsx, showSourceConnectionsModal.css, select-overrides.css, showAggregateReportModal.tsx

### Group 5: Test Fixes
**Why grouped**: All test-related changes
**Issues**:
- 35+ snapshot tests updated (pf-v5 → pf-v6 class names in rendered output)
- ExtendedButton.test.tsx: Updated pf-v5-c-button → pf-v6-c-button assertions
- addSourceModal.test.tsx: Updated pf-v5-c-form__group → pf-v6-c-form__group selectors
- viewLayoutToolbarInteractions.test.tsx: Rewrote to handle PF6 Dropdown portal rendering (use getAllByRole instead of querySelector with OUIA IDs)
**Files**: ExtendedButton.test.tsx, addSourceModal.test.tsx, viewLayoutToolbarInteractions.test.tsx, 32 snapshot files

### Group 6: ESLint False Positive Suppression
**Why grouped**: ESLint import/named rule can't resolve PF6 exports through CSS module chain
**Issues**:
- Added eslint-disable comments for import/named on ~20 files importing from @patternfly/react-core and @patternfly/react-table
- Types verified to exist via tsc --noEmit (passes with 0 errors)
**Files**: 20+ vendor files in react-table-batteries/

## Round Log

### Round 1: All Groups
- Fixed: All 6 groups in single round
- New issues: none
- Build: PASS
- Tests: PASS (265/265)
- Lint: 17 pre-existing issues only (9 display-name, 8 warnings)

## Pre-Migration Steps Applied

1. **pf-codemods**: Ran `npx @patternfly/pf-codemods --v6 --fix` - auto-fixed 23 files
2. **Dependency upgrade**: Updated all @patternfly packages from ^5.x to ^6.x
3. **Visual baseline**: Captured 5 route screenshots (login, credentials, sources, scans, not-found)

## Visual Regression Testing

- **5/5 route screenshots**: Identical between baseline and post-migration
- **0 visual regressions detected**
- **22 interactive components** (modals, dropdowns): Coverage gap - not captured in either baseline or post-migration

## Kantra Analysis

**SKIPPED**: Container runtime (crun/podman) has a system-level permission issue (`sd-bus call: Permission denied`). The nodejs provider requires containers. All migration issues were identified through build errors, lint errors, test failures, and codemod output.

## Complete

- Total rounds: 1
- Build: PASS
- Unit tests: PASS (265/265)
- E2E tests: N/A (none exist)
- Lint: PASS (17 pre-existing issues only)
- Visual regression: PASS (0 regressions in 5 compared screenshots)
- Kantra: SKIPPED (container runtime issue)
- Target validation: PASS

## Action Required

- **Coverage Gap**: 22 interactive UI components (modals, dropdowns, theme variants) were not captured in visual regression testing due to mock API limitations and complex interaction requirements. Manual visual inspection recommended for: credential/source/scan modals, dropdown menus, and dark theme variant.
- **Pre-existing Lint Issues**: 9 `react/display-name` errors in vendor `react-table-batteries` code. These existed before migration and are not caused by the PF5→PF6 upgrade.
- **Kantra Validation Skipped**: Static analysis via Kantra could not run due to system container runtime permissions. If container runtime is fixed, run: `kantra analyze --input ./quipucords-ui --output ./workdir/kantra-final --provider nodejs --source patternfly-v5 --target patternfly-v6 --rules ./rulesets --enable-default-rulesets` to verify zero remaining issues.
