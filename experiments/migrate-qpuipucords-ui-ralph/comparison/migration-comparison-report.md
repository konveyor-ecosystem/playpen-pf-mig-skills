# PatternFly 5 to 6 Migration Comparison Report

**Date:** 2026-02-23
**Agent PR:** [jwmatthews/quipucords-ui#1](https://github.com/jwmatthews/quipucords-ui/pull/1) (AI agent via Ralph loop)
**Golden PR:** [quipucords/quipucords-ui#664](https://github.com/quipucords/quipucords-ui/pull/664) (PatternFly expert, assisted by Cursor AI)

---

## Executive Summary

| Metric | Agent PR | Golden PR |
|--------|----------|-----------|
| Files changed | 71 | 57 |
| Lines added | 1,388 | 770 |
| Lines deleted | 1,374 | 898 |
| Net delta | +14 | -128 |
| Commits | 10 | 4 |
| PF6 version | 6.4.x | 6.3.1 |

The agent successfully completed a functional PF5-to-PF6 migration covering the major API changes. However, several strategic divergences from the golden PR reveal areas where the agent over-migrated in some places (modals), under-migrated in others (icons, table cells, refs), and introduced unnecessary churn (formatting ~20 unrelated files). The golden PR is more surgically precise and follows PF6 idiomatic patterns more consistently.

**Overall alignment score: ~65-70%** -- the agent handled the bulk of mechanical changes correctly but missed several PF6-idiomatic patterns and made some incorrect strategic choices.

---

## 1. Dependencies

| Package | PF5 (Before) | Agent | Golden |
|---------|-------------|-------|--------|
| @patternfly/patternfly | 5.3.1 | 6.4.0 | 6.3.1 |
| @patternfly/react-core | 5.3.4 | 6.4.1 | 6.3.1 |
| @patternfly/react-icons | 5.3.2 | 6.4.0 | 6.3.1 |
| @patternfly/react-styles | 5.3.1 | 6.4.0 | 6.3.1 |
| @patternfly/react-table | 5.3.4 | 6.4.1 | 6.3.1 |

**Verdict:** Both correct. The agent used a newer PF6 point release (6.4.x vs 6.3.1), which is fine.

---

## 2. Modal Migration Strategy (Major Divergence)

This is the single largest strategic difference between the two PRs.

### Agent approach: Full composable Modal migration
The agent migrated every modal to PF6's composable Modal pattern:
```tsx
// Agent: new composable API
<Modal variant={ModalVariant.small} isOpen={isOpen} onClose={onClose}>
  <ModalHeader title="..." />
  <ModalBody>
    {content}
  </ModalBody>
  <ModalFooter>
    {actions}
  </ModalFooter>
</Modal>
```

This restructured the `title` prop into a `<ModalHeader>`, children into `<ModalBody>`, and `actions` into `<ModalFooter>`. This was applied to **every modal** in the application (~8 modals across credentials, scans, and sources views).

### Golden approach: Deprecated Modal import
The golden PR moved the import path to the deprecated re-export:
```tsx
// Golden: deprecated but stable path
import { Modal, ModalVariant } from '@patternfly/react-core/deprecated';
// Usage unchanged from PF5
<Modal variant={ModalVariant.small} title="..." isOpen={isOpen} actions={[...]}>
  {content}
</Modal>
```

### Analysis

| Factor | Agent | Golden |
|--------|-------|--------|
| Code churn | ~300 lines restructured | ~10 lines (import path change) |
| PF6 compliance | Uses new API | Uses deprecated API |
| Risk of breakage | Higher (structural refactoring) | Lower (minimal changes) |
| Future-proofness | Already on new API | Will need migration eventually |
| Files affected | 8 modal files | 8 modal files (import only) |

The golden PR made the pragmatic choice: use the deprecated import path to keep modals working with minimal change. The agent's approach is technically more forward-looking, but it introduced significant structural churn across 8 files, each requiring careful restructuring of title, body, and actions placement. For a migration PR, minimizing churn while maintaining correctness is typically preferred.

**Verdict: Golden is preferred** -- deprecation paths exist specifically to allow incremental migration.

---

## 3. Icon and Color Token Migration (Major Divergence)

### contextIcon.tsx

**Agent approach:** Direct token replacement
```tsx
// Agent: swapped token names, kept same pattern
import {
  t_global_icon_color_100 as gray,
  t_global_icon_color_status_success_default as green,
  t_global_icon_color_status_warning_default as yellow,
  t_global_icon_color_status_danger_default as red
} from '@patternfly/react-tokens';

// Usage unchanged:
<ExclamationCircleIcon {...{ ...{ color: red.value }, ...props }} />
```

**Golden approach:** Idiomatic PF6 `<Icon>` wrapper with `status` prop
```tsx
// Golden: PF6 idiomatic pattern
import { Icon } from '@patternfly/react-core';

// Removed all react-tokens imports, removed ContextIconColors export
<Icon status="danger">
  <ExclamationCircleIcon {...props} />
</Icon>
```

### Analysis

The golden PR follows PF6's recommended pattern: wrap icons in `<Icon status="...">` to apply semantic coloring via CSS, rather than using hardcoded token values. This approach:
- Is theme-aware (automatically handles light/dark mode)
- Follows PF6 component documentation
- Removes the dependency on `@patternfly/react-tokens` for icon colors
- Removes the exported `ContextIconColors` object (breaking change for consumers, but cleaner)

The agent's approach of swapping token names works functionally but is not the PF6 idiomatic pattern and doesn't benefit from automatic theme awareness.

**Verdict: Golden is correct.** The agent missed this migration pattern entirely.

---

## 4. EmptyState Migration

Both PRs correctly migrated away from the PF5 pattern:
```tsx
// PF5 (before)
<EmptyState>
  <EmptyStateHeader titleText="..." icon={<EmptyStateIcon icon={SomeIcon} />} headingLevel="h4" />
  <EmptyStateBody>...</EmptyStateBody>
</EmptyState>
```

**Agent:**
```tsx
<EmptyState headingLevel="h2" titleText="Unable to connect" icon={ExclamationCircleIcon} variant={EmptyStateVariant.sm}>
  <EmptyStateBody>...</EmptyStateBody>
</EmptyState>
```

**Golden:**
```tsx
<EmptyState titleText={<Title headingLevel="h2" size="lg">Unable to connect</Title>}
            icon={ExclamationCircleIcon} variant={EmptyStateVariant.sm}>
  <EmptyStateBody>...</EmptyStateBody>
</EmptyState>
```

### Analysis

The golden PR preserved the `<Title>` wrapper inside `titleText` to retain the `size="lg"` attribute. The agent passed `titleText` as a plain string and used the `headingLevel` prop at the EmptyState level, which loses the explicit size control.

Both approaches are valid PF6 usage. The golden approach is slightly more faithful to the original rendering since it preserves the `size="lg"` specification.

**Verdict:** Both acceptable. Golden is slightly more faithful to original intent.

---

## 5. Masthead / Page Layout

### viewLayout.tsx

Both PRs made the same core changes:
- `MastheadToggle` moved inside `MastheadMain`
- `MastheadLogo` added as wrapper inside `MastheadBrand`
- `Page` prop changed from `header` to `masthead`
- `Nav` and `PageSidebar` `theme="dark"` removed

**Key difference -- sidebar toggle button:**

| Aspect | Agent | Golden |
|--------|-------|--------|
| Component | `<Button icon={<BarsIcon />} variant="plain" .../>` | `<PageToggleButton isHamburgerButton onSidebarToggle={...} />` |
| PF6 compliance | Works, but not idiomatic | Idiomatic PF6 component |

`PageToggleButton` is PF6's purpose-built component for the sidebar toggle. Using it provides proper hamburger menu behavior and accessibility out of the box.

**Verdict: Golden is more correct.** The agent missed the `PageToggleButton` migration.

---

## 6. Toolbar and Dropdown Changes

### viewLayoutToolbar.tsx

Both PRs correctly handled:
- `pf-v5-theme-dark` to `pf-v6-theme-dark`
- `variant="icon-button-group"` to `variant="action-group-plain"`
- `align={{ default: 'alignRight' }}` to `align={{ default: 'alignEnd' }}`
- `spacer` to `gap`
- `data-ouia-component-id` to `ouiaId`

**Divergences:**

| Aspect | Agent | Golden |
|--------|-------|--------|
| DropdownList wrapper | Added `<DropdownList>` around `<DropdownItem>` children | Not added |
| MenuToggle icon | Used `icon` prop: `icon={<QuestionCircleIcon />}` | Kept as children |
| Avatar handling | Kept CSS class: `<span className="pf-v6-c-avatar" />` | Used `<Avatar>` component with `src` import |
| viewLayoutToolbar.css | Updated tokens (kept file) | Deleted entirely |
| User dropdown positioning | No popperProps | Added `popperProps={{ position: 'right' }}` |

The golden PR's Avatar migration is notably cleaner -- it imports the avatar image and uses the PF6 `Avatar` component properly, while the agent just did a class name swap and kept the CSS-based approach.

**Verdict: Golden is cleaner.** The agent's DropdownList wrapper addition may actually be correct for PF6, but the avatar and CSS handling is inferior.

---

## 7. Filter Controls Migration

### MultiselectFilterControl

Both PRs migrated from deprecated `Select` (from `@patternfly/react-core/deprecated`) to the new composable `Select`.

| Feature | Agent | Golden |
|---------|-------|--------|
| Inline filter search | Preserved via `MenuSearch`/`SearchInput` | Dropped |
| Selection count badge | Added `<Badge>` | Used text: `"N selected"` |
| Toggle width | `isFullWidth` | Default width |
| Selected indicator | `isSelected` prop on SelectOption | `isSelected` on SelectOption |
| `hasCheckbox` prop | Yes | No |
| Cleared on close | Yes (`setFilterText('')` in `onOpenChange`) | N/A (no filter) |

The agent's MultiselectFilterControl migration is more feature-complete because it preserves the inline search filtering that existed in PF5's `hasInlineFilter` prop. The golden PR dropped this functionality. This is one area where the agent exceeded the golden PR.

### SelectFilterControl

Both PRs produced similar results -- migrating to the new composable Select with MenuToggle.

**Verdict: Agent is arguably better** for MultiselectFilterControl (preserved filter search). Both are comparable for SelectFilterControl.

---

## 8. Table Cell and Button Changes

| Change | Agent | Golden |
|--------|-------|--------|
| `Td hasAction` prop | Not added | Added on all action cells |
| Button `size="sm"` in tables | Not added | Added for table-inline buttons |
| ActionMenu `size` prop | Not added (no interface change) | Added prop to interface and usage |
| `innerRef` to `ref` (Table/Th/Td/Tr) | Only `useTrWithBatteries` | All 4 files (Table, Th, Td, Tr) |
| `Td isActionCell` | Left unchanged | Changed to `Td hasAction` |

The golden PR added `hasAction` and `size="sm"` systematically to table cells with action buttons. These are PF6 refinements that improve table cell rendering and ensure proper spacing/alignment for action buttons. The agent missed these entirely.

The `innerRef` to `ref` migration was also incomplete in the agent PR (1 of 4 files) vs complete in the golden PR (4 of 4 files).

**Verdict: Golden is significantly more thorough.** The agent missed several table-specific PF6 patterns.

---

## 9. TypeaheadCheckboxes

| Change | Agent | Golden |
|--------|-------|--------|
| `data-ouia-component-id` to `ouiaId` | Done | Done |
| Button icon to `icon` prop | Done | Done |
| `innerRef` to `ref` on MenuToggle | **Not done** | Done |
| `innerRef` to `ref` on TextInputGroupMain | **Not done** | Done |

**Verdict: Golden is more complete.** The agent missed the `innerRef` to `ref` changes on the typeahead component.

---

## 10. CSS and Theming

### app.css

| Change | Agent | Golden |
|--------|-------|--------|
| Formatting cleanup | Reformatted whitespace (noise) | No formatting changes |
| Logo theming CSS | **Not added** | Added 24 lines of logo/modal filter/invert CSS |

The golden PR added critical theming CSS for PF6:
```css
/* Logo inversion for dark-on-light masthead */
.pf-v6-c-masthead__brand .pf-v6-c-brand img {
  filter: invert(1) brightness(1.2);
}
/* Revert in dark mode */
.pf-v6-theme-dark .pf-v6-c-masthead__brand ... {
  filter: none;
}
/* About modal background theming */
.pf-v6-c-about-modal-box { filter: none; }
.pf-v6-theme-dark .pf-v6-c-about-modal-box { filter: invert(1.5) contrast(1.2); }
```

Without these CSS rules, the logo and about modal would not render correctly in PF6's changed theme architecture.

### showSourceConnectionsModal.css

Both correctly updated `pf-v5-*` to `pf-v6-*` and renamed the padding variable. The golden added an additional `PaddingBlockEnd` override.

### select-overrides.css

- Agent: `.isScrollable .pf-v6-c-menu__content` (updated selector for new Select structure)
- Golden: `.pf-v6-c-select.isScrollable .pf-v6-c-select__menu` (kept closer to original structure)

**Verdict: Golden is more complete.** The missing logo theming CSS in the agent PR would result in visual defects.

---

## 11. Test Changes

### viewLayoutToolbarInteractions.test.tsx

| Aspect | Agent | Golden |
|--------|-------|--------|
| Updated | **Not modified** | Significantly rewritten |
| Button queries | Would fail (uses `data-ouia-component-id` selectors) | Uses role-based queries and content matching |
| waitFor usage | N/A | Added proper `waitFor` for async dropdown behavior |

The golden PR rewrote the toolbar interaction tests because PF6's removal of `data-ouia-component-id` automatic passthrough broke the existing selectors. The agent did not touch this file, which means these tests would fail post-migration.

### ExtendedButton.test.tsx

| Aspect | Agent | Golden |
|--------|-------|--------|
| Class names | Updated `pf-v5` to `pf-v6` | Updated `pf-v5` to `pf-v6` |
| Async tests | **Not updated** (missing `async`/`await` on waitFor) | Made tests `async`, added `await waitFor()` |

The golden PR fixed a pre-existing issue: the PF5 tests used `waitFor` without `await`, making them not actually wait for assertions. The golden PR made these tests properly async.

### addSourceModal.test.tsx

| Aspect | Agent | Golden |
|--------|-------|--------|
| Port helper query | Updated `.pf-v5-*` to `.pf-v6-*` class selectors | Used `#source-port-helper-text` id selector |

The golden PR added an `id` prop to `<HelperText>` in the source code and used an id-based selector in tests, which is more resilient than class-based selectors.

**Verdict: Golden is significantly better on test quality.** The agent left broken test selectors and missing async/await.

---

## 12. Unnecessary Changes (Agent-Only)

The agent PR modified ~20 files with formatting-only changes that have nothing to do with PF5-to-PF6 migration:

**Formatting-only changes (no migration value):**
- `src/helpers/queryHelpers.ts` -- line wrapping
- `src/hooks/__tests__/useAlerts.test.ts` -- line wrapping
- `src/hooks/__tests__/useLoginApi.test.ts` -- line wrapping
- `src/hooks/__tests__/useScanApi.test.ts` -- line wrapping
- `src/hooks/__tests__/useStatusApi.test.ts` -- line wrapping
- `src/hooks/useCredentialApi.ts` -- line wrapping
- `src/hooks/useScanApi.ts` -- line wrapping (3 locations)
- `src/hooks/useSourceApi.ts` -- line wrapping
- `src/vendor/.../useActiveItemState.ts` -- line wrapping
- `src/vendor/.../useExpansionState.ts` -- line wrapping
- `src/vendor/.../useFilterState.ts` -- line wrapping
- `src/vendor/.../usePaginationState.ts` -- line wrapping
- `src/vendor/.../useSelectionPropHelpers.ts` -- line wrapping
- `src/vendor/.../useSortState.ts` -- line wrapping
- `src/vendor/.../useTableState.ts` -- line wrapping
- `src/vendor/.../storage/README.md` -- trailing newline
- `src/components/aboutModal/__tests__/aboutModal.test.tsx` -- line wrapping
- `src/components/actionMenu/__tests__/actionMenu.test.tsx` -- line wrapping

These appear to be from an auto-formatter (likely Prettier with a narrower print width). They add noise to the PR (+618/-574 lines of churn), make review harder, and increase the chance of merge conflicts.

**Verdict:** These changes should not be in a migration PR.

---

## 13. Changes Present in Golden but Missing from Agent

| Missing Change | Impact | Severity |
|---------------|--------|----------|
| Logo theming CSS in `app.css` | Logo renders incorrectly in PF6 | High |
| `PageToggleButton` for sidebar toggle | Works but not idiomatic | Medium |
| `Icon` wrapper with `status` for colored icons | Works but not idiomatic; not theme-aware | Medium |
| `Td hasAction` prop on action cells | Minor layout issues | Medium |
| Button/ActionMenu `size="sm"` in tables | Buttons may appear oversized in tables | Medium |
| `innerRef` to `ref` on Table/Th/Td | Deprecation warnings, potential breakage | Medium |
| `innerRef` to `ref` on TypeaheadCheckboxes | Deprecation warnings | Medium |
| `Avatar` component usage | Works but CSS-based approach is fragile | Low |
| Toolbar interaction test fixes | Tests would fail | High |
| ExtendedButton test async/await fixes | Tests might pass but assertions are fire-and-forget | Medium |
| `viewLayoutToolbar.css` deletion | Stale CSS remains | Low |
| `popperProps={{ position: 'right' }}` on user dropdown | Minor positioning issue | Low |
| `Table isExpandable hasAnimations` on connections table | Missing table features | Low |

---

## 14. Changes Present in Agent but Not in Golden

| Extra Change | Assessment |
|-------------|------------|
| Full composable Modal migration (ModalHeader/Body/Footer) | Over-migration; deprecated path was sufficient |
| DropdownList wrapper for Dropdown children | May be needed for PF6 composable Dropdown |
| MultiselectFilter inline search preservation | Better than golden (preserved feature) |
| Badge for filter selection count | Nice enhancement |
| MenuToggle `icon` prop usage | Correct PF6 pattern (golden kept children) |
| ~20 files of auto-formatting | Unnecessary noise |

---

## 15. File-by-File Alignment Matrix

| File | Agent Correct | Agent Divergent | Agent Missing | Notes |
|------|:---:|:---:|:---:|-------|
| package.json | Y | - | - | Both correct |
| app.css | - | Formatting | Logo/modal theming CSS | Missing critical CSS |
| aboutModal.tsx | Y | - | - | Identical migration |
| actionMenu.tsx | Y | icon prop style | size prop | Missing size support |
| contextIcon.tsx | - | Token swap | Icon wrapper pattern | Wrong approach |
| errorMessage.tsx | Y | titleText style | - | Minor difference |
| simpleDropdown.tsx | Y | - | - | Identical |
| typeaheadCheckboxes.tsx | Y | - | innerRef to ref | Incomplete |
| viewLayout.tsx | Y | Button vs PageToggleButton | - | Missing PF6 component |
| viewLayoutToolbar.css | - | Updated vs deleted | - | Should have been deleted |
| viewLayoutToolbar.tsx | Partial | DropdownList, avatar approach | popperProps, Avatar import | Several differences |
| FilterToolbar.tsx | Y | DropdownList addition | - | Mostly correct |
| MultiselectFilterControl.tsx | Y | Preserved filter search | - | Better than golden |
| SelectFilterControl.tsx | Y | - | - | Both correct |
| SearchFilterControl.tsx | Y | - | - | Both correct |
| NoDataEmptyState.tsx | Y | - | - | Both correct |
| StateError.tsx | Y | - | - | Both correct, lost color |
| ToolbarBulkSelector.tsx | Y | - | - | Both correct |
| addCredentialModal.tsx | - | Full Modal migration | deprecated import path | Over-migration |
| viewCredentialsList.tsx | Partial | Modal refactoring | hasAction, size="sm" | Incomplete |
| viewScansList.tsx | Partial | Modal refactoring | hasAction, size="sm" | Incomplete |
| viewSourcesList.tsx | Partial | Modal refactoring | hasAction, size="sm" | Incomplete |
| notFound.tsx | Y | - | - | Identical |
| showScansModal.tsx | - | Full Modal migration | deprecated import path | Over-migration |
| showAggregateReportModal.tsx | - | Full Modal migration | deprecated import path | Over-migration |
| addSourceModal.tsx | - | Full Modal migration | HelperText id, deprecated path | Over-migration |
| addSourcesScanModal.tsx | - | Full Modal migration | deprecated import path | Over-migration |
| showSourceConnectionsModal.tsx | - | Full Modal migration | isExpandable, deprecated path | Over-migration |
| useTrWithBatteries.tsx | Partial | Formatting noise | - | Incomplete ref change |
| useTable/Th/TdWithBatteries.tsx | - | Not touched | innerRef to ref | Missing |
| usePaginationPropHelpers.ts | Y | - | - | Both correct |
| select-overrides.css | Y | Different selector | - | Both work |
| ExtendedButton test | Partial | - | async/await fix | Missing test quality fix |
| viewLayoutToolbar test | - | Not touched | Complete rewrite needed | Tests would fail |

---

## 16. Recommendations for Migration Tooling

Based on this comparison, the following improvements would bring the agent migration closer to expert quality:

1. **Use deprecated import paths for Modal** rather than full composable migration. This dramatically reduces churn.
2. **Teach the `<Icon status="...">` pattern** for colored icons. This is a fundamental PF6 pattern the agent missed.
3. **Add `hasAction` and `size="sm"` rules** for buttons inside table cells.
4. **Complete `innerRef` to `ref` migration** across all table-related components.
5. **Add `PageToggleButton` migration rule** for sidebar toggle buttons.
6. **Add theming CSS rules** for logo and about modal (or detect when custom dark-mode CSS is needed).
7. **Suppress auto-formatting** on unchanged files during migration. Only format files that have actual migration changes.
8. **Update test selectors** that rely on `data-ouia-component-id` which PF6 no longer passes through.
9. **Fix async test patterns** (add `await` to `waitFor` calls).
10. **Use `Avatar` component** instead of CSS-based avatar patterns.

---

## 17. Conclusion

The agent-driven migration achieved a working PF5-to-PF6 upgrade with the core mechanical changes handled correctly. The most significant gaps are in PF6-idiomatic patterns (Icon status wrapping, PageToggleButton, Avatar component) and in migration strategy (full Modal restructuring vs. deprecated path). The excessive formatting changes also reduced the signal-to-noise ratio of the PR.

The golden PR demonstrates that an expert migration prioritizes:
1. Minimal churn (use deprecated paths where available)
2. Idiomatic patterns (Icon status, PageToggleButton, Avatar)
3. Thorough detail work (hasAction, size props, ref changes)
4. Test resilience (selector updates, async fixes)
5. Visual correctness (theming CSS)

These priorities should inform future iterations of the migration agent's skills and rules.
