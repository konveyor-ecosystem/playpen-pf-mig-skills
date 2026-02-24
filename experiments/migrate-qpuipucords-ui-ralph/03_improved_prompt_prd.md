# PRD: Quipucords UI — PatternFly 5 to PatternFly 6 Migration

## Introduction

Migrate the **quipucords-ui** application (located at `./quipucords-ui`) from PatternFly 5 to PatternFly 6. The application is a React 18.3.1 + TypeScript (strict mode) SPA bundled with Webpack via Weldable, tested with Jest 29.7.0 + @testing-library/react. The migration must preserve all existing functionality, pass all quality checks, and maintain 80% line/function coverage thresholds.

The work is broken into 10 sequential user stories, each designed to be completable by an autonomous AI agent in a single session. **Stories must be executed in order** — each builds on the previous.

## Goals

- Update all PatternFly dependencies from v5 to v6
- Resolve all breaking API changes across components, CSS, and tokens
- Migrate deprecated components (Select, Modal, EmptyState, Text) to PF6 equivalents
- Ensure all 33 test files pass with required coverage thresholds
- Produce a clean, buildable application with zero PF5 remnants

## Application Context

- **Framework:** React 18.3.1 with TypeScript (strict mode)
- **Bundler:** Webpack via Weldable
- **Testing:** Jest 29.7.0 + @testing-library/react
- **Current PatternFly 5 packages:**
  - `@patternfly/patternfly`: 5.3.1
  - `@patternfly/react-core`: 5.3.4
  - `@patternfly/react-icons`: 5.3.2
  - `@patternfly/react-styles`: 5.3.1
  - `@patternfly/react-table`: 5.3.4
- **Key directories:**
  - `/src/components/` — 12 reusable UI component directories
  - `/src/views/` — 3 main views (sources, scans, credentials) with modals
  - `/src/hooks/` — 6 custom hooks for API interactions
  - `/src/vendor/react-table-batteries/` — Forked table utilities using deprecated PF Select components
- **33 test files** with coverage thresholds: branches 60%, functions 80%, lines 80%, statements 80%

## Migration Reference

### Codemod Tools (Run in Order)

1. **Main codemods** (`@patternfly/pf-codemods`): Handles React component API changes.
   ```bash
   npx @patternfly/pf-codemods@latest ./src --v6 --fix
   ```
2. **Class name updater** (`@patternfly/class-name-updater`): Updates CSS class prefixes.
   ```bash
   npx @patternfly/class-name-updater ./src --v6 --fix
   ```
3. **CSS vars updater** (`@patternfly/css-vars-updater`): Updates CSS variables in stylesheets.
   ```bash
   npx @patternfly/css-vars-updater ./src --fix
   ```

### Key Breaking Changes

| Component | Change |
|-----------|--------|
| **EmptyState** | `EmptyStateHeader`/`EmptyStateIcon` removed; use `titleText`, `headingLevel`, `icon`, `status` props on `EmptyState` |
| **Text/TextContent** | All replaced with single `Content` component |
| **Button** | Icons must use `icon` prop; `isActive` → `isClicked` |
| **Masthead** | `MastheadBrand` → `MastheadLogo`; new `MastheadBrand` wraps `MastheadLogo`; both inside `MastheadMain` |
| **Page** | `header` → `masthead`; `isTertiaryNavGrouped` → `isHorizontalSubnavGrouped` |
| **Nav** | `"tertiary"` → `"horizontal-subnav"`; `theme` removed |
| **Modal** | Old Modal deprecated; "next" Modal auto-promoted |
| **Toolbar** | "Chip" references → "Label" |
| **Select (deprecated)** | Must migrate to composable Select or SelectTemplate |
| **Label** | `"cyan"` → `"teal"`, `"gold"` → `"yellow"` |
| **PageSidebar** | `theme` removed |
| **FormGroup** | `labelIcon` → `labelHelp` |
| **HelperTextItem** | `hasIcon`/`isDynamic` removed; icon renders automatically with non-default `variant` |

### CSS/Token Changes

- Class prefixes: `pf-v5-c-*` → `pf-v6-c-*`, `pf-v5-u-*` → `pf-v6-u-*`, `pf-v5-l-*` → `pf-v6-l-*`
- Token naming: `--pf-v5-global--*` → `--pf-t--global--*`
- React tokens: `t_` prefix (e.g., `t_global_spacer_sm`) from `@patternfly/react-tokens`
- Directional: `Left` → `InsetInlineStart`, `Right` → `InsetInlineEnd`
- Breakpoints: rem units instead of pixels (divide px by 16)

### Fully Removed in PF6

Application Launcher, Context Selector, old Dropdown, Options Menu, Page Header, old Select, KebabToggle, PageNavigation

### Deprecated but Available at `@patternfly/react-core/deprecated`

Chip → Label; ChipGroup → LabelGroup; Tile → Card; DragDrop → DragDropSort; old DualListSelector; old Modal (auto-promoted)

---

## User Stories

### US-001: Update Dependencies and Run Codemods

**Description:** As a developer, I want to update all PatternFly packages to v6 and run automated codemods so that mechanical transformations are applied before manual work begins.

**Acceptance Criteria:**
- [ ] All `@patternfly/*` packages in `package.json` updated to latest 6.x (all using same minor version)
- [ ] `npm install` completes successfully
- [ ] Main codemods applied: `NODE_OPTIONS=--max-old-space-size=4096 npx @patternfly/pf-codemods@latest ./src --v6 --fix`
- [ ] Class name updater applied: `npx @patternfly/class-name-updater ./src --v6 --fix`
- [ ] CSS vars updater applied: `npx @patternfly/css-vars-updater ./src --fix`
- [ ] Codemod output reviewed and committed as a checkpoint
- [ ] Remaining TypeScript errors from `npm run test:types` are recorded (these will be fixed in subsequent stories)

**Technical Notes:**
- Use `npm info @patternfly/react-core versions` to find latest v6 versions.
- Use `NODE_OPTIONS=--max-old-space-size=4096` if memory issues occur during codemods.
- The codemods handle: prop renames (`isActive` → `isClicked`), component restructuring hints, CSS class prefix updates, CSS variable name updates, some color token replacements (others become `--pf-t--temp--dev--tbd` placeholders).
- Run a dry run first (`npx @patternfly/pf-codemods@latest ./src --v6` without `--fix`) to preview changes.

---

### US-002: Fix Core Layout — Masthead, Page, Navigation, Sidebar

**Description:** As a developer, I want to fix the main application layout components that changed structurally in PF6 so that the app shell renders correctly.

**Files to modify:**
- `src/components/viewLayout/viewLayout.tsx`
- `src/components/viewLayout/viewLayoutToolbar.tsx`
- `src/components/viewLayout/viewLayoutToolbar.css`
- Related test files and snapshots in `src/components/viewLayout/__tests__/`

**Acceptance Criteria:**
- [ ] `MastheadBrand` renamed to `MastheadLogo` (component holding logo/brand image)
- [ ] New `MastheadBrand` component wraps `MastheadLogo`
- [ ] `MastheadToggle` and `MastheadBrand` are both inside `MastheadMain`
- [ ] All new component names imported from `@patternfly/react-core`
- [ ] `Page` prop `header` renamed to `masthead`
- [ ] `isTertiaryNavGrouped` renamed to `isHorizontalSubnavGrouped` (if used)
- [ ] `isTertiaryNavWidthLimited` renamed to `isHorizontalSubnavWidthLimited` (if used)
- [ ] `tertiaryNav` renamed to `horizontalSubnav` (if used)
- [ ] `PageSidebar` `theme` prop removed (if present)
- [ ] `Nav` `variant="tertiary"` changed to `variant="horizontal-subnav"` (if used)
- [ ] `Nav` `theme` prop removed (if present)
- [ ] CSS in `viewLayoutToolbar.css`: all `pf-v5-` prefixes updated to `pf-v6-`; `--pf-v5-` CSS variables updated to PF6 equivalents; avatar styling override reviewed
- [ ] Base CSS import in `src/app.tsx` verified (`@patternfly/react-core/dist/styles/base.css` path confirmed for PF6)
- [ ] Tests updated and snapshots regenerated: `npx jest --roots=./src -u --testPathPattern viewLayout`
- [ ] `npm run test:types` passes for layout files
- [ ] Layout-related tests pass
- [ ] Verify in browser that app shell renders correctly (masthead, sidebar, navigation)

---

### US-003: Migrate EmptyState Components

**Description:** As a developer, I want to replace all `EmptyStateHeader` and `EmptyStateIcon` usage with the PF6 EmptyState API so that empty state displays compile and render correctly.

**Files to modify:**
- `src/views/sources/viewSourcesList.tsx`
- `src/views/scans/showScansModal.tsx`
- `src/views/scans/viewScansList.tsx`
- `src/views/credentials/viewCredentialsList.tsx`
- `src/views/notFound/notFound.tsx`
- `src/components/errorMessage/errorMessage.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/TableControls/NoDataEmptyState.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/TableControls/StateError.tsx`
- Related test files and snapshots

**Acceptance Criteria:**
- [ ] No imports of `EmptyStateHeader` or `EmptyStateIcon` remain in any file
- [ ] `titleText` and `headingLevel` are props on `EmptyState` (not on a child component)
- [ ] `icon` prop on `EmptyState` receives the icon component reference directly (not a JSX element)
- [ ] `EmptyStateBody`, `EmptyStateFooter`, `EmptyStateActions` remain as children
- [ ] All related test files updated and snapshots regenerated
- [ ] `npm run test:types` passes
- [ ] EmptyState-related tests pass
- [ ] Verify in browser that empty states render correctly on sources, scans, and credentials views

**PF6 pattern:**
```tsx
// PF5 (old)
<EmptyState>
  <EmptyStateHeader titleText="Title" headingLevel="h4" icon={<EmptyStateIcon icon={CubesIcon} />} />
  <EmptyStateBody>Body text</EmptyStateBody>
</EmptyState>

// PF6 (new)
<EmptyState titleText="Title" headingLevel="h4" icon={CubesIcon} variant={EmptyStateVariant.sm}>
  <EmptyStateBody>Body text</EmptyStateBody>
</EmptyState>
```

---

### US-004: Migrate Text/TextContent to Content Component

**Description:** As a developer, I want to replace all `Text`, `TextContent`, `TextList`, and `TextListItem` usage with the PF6 `Content` component so that text rendering compiles correctly.

**Files to modify:**
- `src/components/aboutModal/aboutModal.tsx`
- Any other files using `Text`, `TextContent`, `TextList`, `TextListItem`
- Related test files and snapshots

**Acceptance Criteria:**
- [ ] No imports of `Text`, `TextContent`, `TextList`, `TextListItem`, `TextVariants`, `TextListVariants`, or `TextListItemVariants` remain
- [ ] `Content` and `ContentVariants` imported from `@patternfly/react-core` where needed
- [ ] `<TextContent>` replaced with `<Content>`
- [ ] `<Text component="...">` replaced with `<Content component="...">`
- [ ] `<TextList>` replaced with `<Content component={ContentVariants.ul}>` (or `ol`)
- [ ] `<TextListItem>` replaced with `<Content component="li">`
- [ ] `isVisited` prop replaced with `isVisitedLink` (if used)
- [ ] `isPlain` prop replaced with `isPlainList` (if used)
- [ ] Tests updated and snapshots regenerated
- [ ] `npm run test:types` passes
- [ ] About modal tests pass
- [ ] Verify in browser that about modal renders text correctly

---

### US-005: Migrate Modal Components

**Description:** As a developer, I want to migrate all Modal usage to the PF6 Modal API so that all dialogs compile and function correctly.

**Files to modify (10 source files):**
- `src/components/aboutModal/aboutModal.tsx`
- `src/components/viewLayout/viewLayoutToolbar.tsx`
- `src/views/sources/addSourceModal.tsx`
- `src/views/sources/addSourcesScanModal.tsx`
- `src/views/sources/showSourceConnectionsModal.tsx`
- `src/views/scans/showScansModal.tsx`
- `src/views/scans/showAggregateReportModal.tsx`
- `src/views/credentials/addCredentialModal.tsx`
- `src/views/credentials/viewCredentialsList.tsx`
- `src/views/scans/viewScansList.tsx`
- Related test files and snapshots

**Acceptance Criteria:**
- [ ] All Modal imports reference PF6 Modal (not deprecated path)
- [ ] `variant` prop values match PF6 `ModalVariant` enum
- [ ] `title` prop updated to `titleText` if PF6 API requires it
- [ ] `onClose` callback signature verified against PF6 API
- [ ] `appendTo` usage reviewed (PF6 Modal renders to `document.body` by default)
- [ ] `AboutModal` (`PfAboutModal` alias) verified as exported from `@patternfly/react-core` in PF6
- [ ] Tests updated — modal rendering tests may need `{ hidden: true }` or `baseElement` queries since content renders to `document.body`
- [ ] All affected snapshots regenerated
- [ ] `npm run test:types` passes
- [ ] All modal-related tests pass
- [ ] Verify in browser that modals open, display content, and close correctly

---

### US-006: Migrate Button, FormGroup, and Miscellaneous Component Changes

**Description:** As a developer, I want to fix remaining component API changes not handled by codemods so that all component props match PF6 expectations.

**Acceptance Criteria:**
- [ ] **Button:** Icons passed as children moved to `icon` prop; `isActive` renamed to `isClicked` (if used). All `<Button` usage searched and verified.
- [ ] **FormGroup:** `labelIcon` prop renamed to `labelHelp` in all form components
- [ ] **HelperTextItem:** `hasIcon` and `isDynamic` props removed (icon renders automatically with non-default `variant`)
- [ ] **Checkbox/Radio:** `isLabelBeforeButton` replaced with `labelPosition="start"` (if used)
- [ ] **MenuToggle:** Icons use `icon` prop instead of children (if applicable)
- [ ] **NavItem:** `hasNavLinkWrapper` prop removed; icons passed to `icon` prop (if used)
- [ ] **Title:** Component API verified against PF6 (size values may differ)
- [ ] All related tests updated and snapshots regenerated
- [ ] `npm run test:types` passes
- [ ] All affected component tests pass
- [ ] Verify in browser that buttons, forms, and navigation items render correctly

**Button migration pattern:**
```tsx
// PF5
<Button variant="plain"><TimesIcon /></Button>

// PF6
<Button variant="plain" icon={<TimesIcon />} />
```

---

### US-007: Migrate Vendor Code — React Table Batteries and Deprecated Select

**Description:** As a developer, I want to migrate the vendored react-table-batteries code and replace all deprecated Select components with PF6 composable Select so that filter controls compile and work correctly.

**Files to modify:**
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/MultiselectFilterControl.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/SelectFilterControl.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/FilterToolbar.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/select-overrides.css`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/TableControls/NoDataEmptyState.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/TableControls/StateError.tsx`
- Any other vendor files with PF5 dependencies
- Related test files

**Acceptance Criteria:**
- [ ] No imports from `@patternfly/react-core/deprecated` remain in vendor code
- [ ] `SelectFilterControl.tsx` rewritten to use composable Select (`Select`, `SelectOption`, `SelectList`, `MenuToggle`, `MenuToggleElement` from `@patternfly/react-core`)
- [ ] `MultiselectFilterControl.tsx` rewritten to use composable Select with `hasCheckbox` and `isSelected` on `SelectOption`
- [ ] `FilterToolbar.tsx` no longer imports `SelectOptionProps` from deprecated path; uses PF6 equivalent types
- [ ] `select-overrides.css` updated with PF6 class selectors or removed if no longer needed
- [ ] EmptyState in vendor TableControls confirmed fixed (should have been done in US-003)
- [ ] All other PF5-specific patterns in vendor code resolved
- [ ] Tests updated and snapshots regenerated
- [ ] `npm run test:types` passes
- [ ] Vendor-related tests pass
- [ ] Verify in browser that filter controls in table views work correctly (single-select and multi-select)

**Single-select pattern (PF6):**
```tsx
import { Select, SelectOption, SelectList, MenuToggle, MenuToggleElement } from '@patternfly/react-core';

<Select
  isOpen={isOpen}
  onSelect={onSelect}
  onOpenChange={setIsOpen}
  toggle={(toggleRef: React.Ref<MenuToggleElement>) => (
    <MenuToggle ref={toggleRef} onClick={() => setIsOpen(!isOpen)} isExpanded={isOpen}>
      {selected || 'Select...'}
    </MenuToggle>
  )}
>
  <SelectList>
    {options.map(opt => <SelectOption key={opt} value={opt}>{opt}</SelectOption>)}
  </SelectList>
</Select>
```

**Multi-select pattern (PF6):**
```tsx
<Select
  role="menu"
  isOpen={isOpen}
  onSelect={(_event, value) => handleSelect(value)}
  onOpenChange={setIsOpen}
  toggle={...}
>
  <SelectList>
    {options.map(opt => (
      <SelectOption key={opt} value={opt} hasCheckbox isSelected={selected.includes(opt)}>
        {opt}
      </SelectOption>
    ))}
  </SelectList>
</Select>
```

---

### US-008: Migrate Application Select/Dropdown Components

**Description:** As a developer, I want to migrate remaining Select and Dropdown components in the main application code so that all interactive controls use PF6 APIs.

**Files to check:**
- `src/components/simpleDropdown/simpleDropdown.tsx`
- `src/components/typeAheadCheckboxes/typeaheadCheckboxes.tsx`
- `src/components/actionMenu/actionMenu.tsx`
- Any other components using Dropdown or Select patterns
- Related test files and snapshots

**Acceptance Criteria:**
- [ ] **SimpleDropdown:** If using old Dropdown API, migrated to PF6 composable Dropdown (`Dropdown`, `DropdownItem`, `DropdownList`, `MenuToggle` from `@patternfly/react-core`)
- [ ] **TypeAheadCheckboxes:** If using deprecated Select with typeahead, migrated to PF6 composable Select with `TextInput` in toggle
- [ ] **ActionMenu:** Dropdown/MenuToggle usage is PF6 compatible; `EllipsisVIcon` uses `icon` prop on `MenuToggle`
- [ ] No imports from `@patternfly/react-core/deprecated` remain in application component code
- [ ] All related tests updated and snapshots regenerated
- [ ] `npm run test:types` passes
- [ ] Component tests pass
- [ ] Verify in browser that dropdowns and select controls work correctly across the application

---

### US-009: CSS Cleanup, Token Resolution, and Styling Fixes

**Description:** As a developer, I want to resolve all remaining CSS and design token issues so that no PF5 references or placeholder tokens remain.

**Files to check:**
- `src/app.css`
- `src/components/viewLayout/viewLayoutToolbar.css`
- `src/views/sources/showSourceConnectionsModal.css`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/select-overrides.css`
- Any `.tsx` files referencing PF CSS classes or variables inline

**Acceptance Criteria:**
- [ ] Zero `--pf-t--temp--dev--tbd` placeholder tokens remain in any file (each resolved to correct PF6 semantic token)
- [ ] Zero `pf-v5-` class name references remain in any source file
- [ ] Zero `--pf-v5-` CSS variable references remain in any source file
- [ ] Custom CSS overrides reviewed and updated: `viewLayoutToolbar.css` (avatar, toolbar), `showSourceConnectionsModal.css` (modal styles), `select-overrides.css` (filter menu), `app.css` (global styles)
- [ ] PatternFly CSS import paths verified in `app.tsx`: `@patternfly/react-core/dist/styles/base.css` and `@patternfly/react-styles/css/components/Avatar/avatar.css`
- [ ] `@patternfly/react-tokens` imports updated to `t_` prefix naming (e.g., `t_global_spacer_sm`)
- [ ] Any hardcoded pixel breakpoint values in JS/TS converted to rem (divide by 16)
- [ ] `npm run test:types` passes
- [ ] Verify in browser that styling appears correct across all views

**Token resolution approach:**
For each `--pf-t--temp--dev--tbd` placeholder:
1. Read the comment noting the original PF5 token
2. Find the closest PF6 semantic token from the [PF6 token catalog](https://www.patternfly.org/tokens/all-patternfly-tokens)
3. Replace the placeholder

---

### US-010: Test Suite Fixes and Final Verification

**Description:** As a developer, I want all 33 test files to pass and the application to build successfully so that the migration is complete and verified.

**Acceptance Criteria:**
- [ ] `npm run test:types` passes with zero errors
- [ ] `npm run test:lint` passes with zero errors
- [ ] `npm run test:ci-coverage` passes — all 33 test files green
- [ ] Coverage thresholds met: branches ≥60%, functions ≥80%, lines ≥80%, statements ≥80%
- [ ] `npm run build` completes successfully
- [ ] `npm run test:integration` passes (if applicable)
- [ ] No snapshot files contain stale PF5 references
- [ ] Verify in browser that all major views render: sources list, scans list, credentials list, modals, empty states, error states

**Common test fixes for PF6:**
- **Snapshot failures:** Delete old snapshots and regenerate with `npx jest -u`
- **Query failures:** Tests using `getByText`/`getByRole` may fail due to changed DOM structure, class names (`v5` → `v6`), or component structure changes
- **Portal rendering:** For Select/Dropdown/Modal content rendered to `document.body`, use `{ hidden: true }` in queries or `screen.getByRole` which searches the whole document
- **Import failures:** Verify test files don't import removed components
- **Type errors:** Fix any `@types` mismatches

---

## Functional Requirements

- FR-1: All `@patternfly/*` dependencies updated to latest compatible 6.x versions
- FR-2: All PatternFly codemods executed (pf-codemods, class-name-updater, css-vars-updater) before manual changes
- FR-3: Masthead/Page/Nav/Sidebar restructured per PF6 API (MastheadLogo, masthead prop, horizontal-subnav)
- FR-4: All EmptyState usage migrated to props-based API (no EmptyStateHeader/EmptyStateIcon)
- FR-5: All Text/TextContent/TextList replaced with Content component
- FR-6: All Modal usage migrated to PF6 promoted Modal API
- FR-7: All Button icon children moved to `icon` prop; FormGroup `labelIcon` → `labelHelp`
- FR-8: All deprecated Select/Dropdown components replaced with PF6 composable equivalents
- FR-9: All CSS classes, variables, and tokens updated from PF5 to PF6 naming
- FR-10: All 33 test files pass with required coverage thresholds; application builds successfully

## Non-Goals

- No functional changes to application behavior — this is a library upgrade only
- No new features or UX changes
- No dependency upgrades beyond PatternFly packages
- No refactoring of application architecture or component structure beyond what PF6 requires
- No changes to build tooling (Webpack/Weldable configuration)
- No changes to CI/CD pipeline configuration

## Technical Considerations

- **Execution order matters.** Stories must be completed sequentially (US-001 through US-010). Each builds on the previous.
- **Vendor code** (`src/vendor/`) is part of this codebase and must be migrated as application code.
- **Codemods first.** US-001 runs automated codemods before any manual work. If a codemod produces incorrect output, fix it manually rather than reverting.
- **Snapshot strategy:** Delete and regenerate snapshots (`npx jest -u`) rather than manually editing `.snap` files.
- **Commit after each story** with message format: `feat: [Story ID] - [Story Title]`
- **If an issue cannot be resolved**, document it clearly and move to the next story for follow-up.

## Success Metrics

- Zero TypeScript errors (`npm run test:types` exits 0)
- Zero lint errors (`npm run test:lint` exits 0)
- All 33 test files pass (`npm run test:ci-coverage` exits 0)
- Coverage thresholds met: branches ≥60%, functions ≥80%, lines ≥80%, statements ≥80%
- Application builds successfully (`npm run build` exits 0)
- Zero remaining PF5 references: no `pf-v5-` classes, no `--pf-v5-` variables, no `--pf-t--temp--dev--tbd` placeholders
- No imports from removed PF5 components
- All views render correctly in browser

## Open Questions

- Are there any PF5 components used that are not documented in the breaking changes table above? A full grep for `@patternfly` imports should be done in US-001 to catalog all usage.
- Does the `@patternfly/react-core/dist/styles/base.css` import path exist in PF6, or has it moved?
- Are there any Weldable/Webpack configuration changes needed for PF6 CSS processing?
- Does the vendored react-table-batteries code have upstream PF6 compatibility that could be referenced?
