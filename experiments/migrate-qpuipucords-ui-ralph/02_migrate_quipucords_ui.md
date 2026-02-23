# Quipucords UI: PatternFly 5 to PatternFly 6 Migration Plan

## Overview

This document is a prompt for an AI coding agent to migrate the **quipucords-ui** application (located at `./quipucords-ui`) from PatternFly 5 to PatternFly 6. The migration is broken into discrete, sequential units of work, each designed to be completable by an AI agent in a single session (under 100k tokens).

**Execute units in order.** Each unit builds on the previous. After completing each unit, verify the application compiles (`npm run test:types`) and run any applicable tests before proceeding to the next unit.

---

## Application Summary

- **Framework:** React 18.3.1 with TypeScript (strict mode)
- **Bundler:** Webpack via Weldable
- **Testing:** Jest 29.7.0 + @testing-library/react
- **PatternFly 5 packages:**
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
- **33 test files** with 80% line/function coverage requirements

---

## Research Reference: PatternFly 6 Migration Guidance

The following sections document the official PF5→PF6 migration guidance. Refer to these when executing each unit of work.

### Upgrade Process (5 Steps)

1. **Update dependencies** to PF6 packages (manual)
2. **Run the codemods suite** BEFORE making any manual changes
3. **Remove CSS overrides** targeting outdated PF5 styles
4. **Review variable and class name changes**
5. **Convert pixel-based breakpoint logic** to rem units

### Codemod Tools (Run in Order)

#### 1. Main Codemods (`@patternfly/pf-codemods`)
Handles React component API changes (prop renames, removals, restructuring).
```bash
npx @patternfly/pf-codemods@latest ./src --v6 --fix
```
Use `NODE_OPTIONS=--max-old-space-size=4096` if memory issues occur.

#### 2. Class Name Updater (`@patternfly/class-name-updater`)
Updates hardcoded CSS class names (`pf-v5-c-*` → `pf-v6-c-*`, etc.).
```bash
npx @patternfly/class-name-updater ./src --v6 --fix
```

#### 3. Token Updater (part of pf-codemods)
Updates React token imports and CSS variable references in JS/TSX files. Color tokens are replaced with a placeholder (`--pf-t--temp--dev--tbd`) requiring manual resolution.

#### 4. CSS Vars Updater (`@patternfly/css-vars-updater`)
Updates CSS variables in `.css`, `.scss`, `.less` files.
```bash
npx @patternfly/css-vars-updater ./src --fix
```

### Component Breaking Changes Relevant to This App

| Component | Change | Files Affected |
|-----------|--------|---------------|
| **EmptyState** | `EmptyStateHeader` and `EmptyStateIcon` removed as separate components; use props on `EmptyState` (`titleText`, `headingLevel`, `icon`, `status`) | 6 source files + snapshots |
| **Text/TextContent/TextList/TextListItem** | All replaced with single `Content` component | `aboutModal.tsx` + snapshot |
| **Button** | Icons must use `icon` prop instead of children; `isActive` → `isClicked` | Multiple files |
| **Masthead** | `MastheadBrand` renamed to `MastheadLogo`; new `MastheadBrand` wraps `MastheadLogo`; `MastheadToggle` and `MastheadBrand` wrapped in `MastheadMain` | `viewLayout.tsx` + snapshots |
| **Page** | `header` → `masthead`; `isTertiaryNavGrouped` → `isHorizontalSubnavGrouped` | `viewLayout.tsx` |
| **Nav** | `"tertiary"` variant removed, use `"horizontal-subnav"`; `theme` prop removed | `viewLayout.tsx` |
| **Modal** | Old Modal deprecated; new "next" Modal auto-promoted | 10 source files + tests + snapshots |
| **Toolbar** | All "Chip" references renamed to "Label" (props, interfaces) | Vendor code primarily |
| **Select (deprecated)** | Must migrate to composable Select or SelectTemplate | 3 vendor files |
| **Label** | Color values: `"cyan"` → `"teal"`, `"gold"` → `"yellow"` | Check all Label usage |
| **PageSidebar** | `theme` prop removed | `viewLayout.tsx` |
| **Switch** | `labelOff` prop removed | Check all Switch usage |
| **FormGroup** | `labelIcon` → `labelHelp` | Check form components |
| **HelperTextItem** | `hasIcon` and `isDynamic` removed; icon renders automatically with non-default `variant` | Check form components |

### CSS and Token Changes

- **Class prefixes:** `pf-v5-c-*` → `pf-v6-c-*`, `pf-v5-u-*` → `pf-v6-u-*`, `pf-v5-l-*` → `pf-v6-l-*`
- **Token naming:** `--pf-v5-global--*` → `--pf-t--global--*` (semantic tokens)
- **React tokens:** Use `t_` prefix (e.g., `t_global_spacer_sm`) imported from `@patternfly/react-tokens`
- **Directional properties:** `Left` → `InsetInlineStart`, `Right` → `InsetInlineEnd`
- **Breakpoints:** Now use rem units instead of pixels (divide px by 16)

### Removed/Deprecated Components

These are **fully removed** in PF6 (were deprecated in PF5):
- Application Launcher, Context Selector, old Dropdown, Options Menu, Page Header, old Select, KebabToggle, PageNavigation

These are **deprecated but still available** at `@patternfly/react-core/deprecated`:
- Chip → migrate to Label; ChipGroup → migrate to LabelGroup
- Tile → migrate to Card
- DragDrop → migrate to DragDropSort
- Old DualListSelector, old Modal → new "next" versions auto-promoted

---

## Migration Units of Work

### Unit 1: Update Dependencies and Run Codemods

**Goal:** Update all PatternFly packages to v6 and run automated codemods to handle mechanical transformations.

**Steps:**

1. **Update PatternFly dependencies in `package.json`:**
   - `@patternfly/patternfly`: update to latest 6.x
   - `@patternfly/react-core`: update to latest 6.x
   - `@patternfly/react-icons`: update to latest 6.x
   - `@patternfly/react-styles`: update to latest 6.x
   - `@patternfly/react-table`: update to latest 6.x

   Use `npm info @patternfly/react-core versions` (or check npm registry) to find the latest v6 versions. All `@patternfly/*` packages should use the same minor version for compatibility.

2. **Install updated dependencies:**
   ```bash
   npm install
   ```

3. **Run the main codemods (dry run first, then fix):**
   ```bash
   # Dry run to see what will change
   npx @patternfly/pf-codemods@latest ./src --v6

   # Apply fixes
   NODE_OPTIONS=--max-old-space-size=4096 npx @patternfly/pf-codemods@latest ./src --v6 --fix
   ```

4. **Run the class name updater:**
   ```bash
   npx @patternfly/class-name-updater ./src --v6 --fix
   ```

5. **Run the CSS vars updater on CSS files:**
   ```bash
   npx @patternfly/css-vars-updater ./src --fix
   ```

6. **Review codemod output.** The codemods will handle many mechanical changes:
   - Prop renames (e.g., `isActive` → `isClicked` on Button)
   - Component restructuring hints (e.g., EmptyState)
   - CSS class prefix updates
   - CSS variable name updates
   - Some color token replacements (others become `--pf-t--temp--dev--tbd` placeholders)

7. **Attempt a type check:**
   ```bash
   npm run test:types
   ```
   Record the remaining TypeScript errors — these will be addressed in subsequent units.

8. **Commit the raw codemod output** as a checkpoint before manual work begins.

**Verification:** `npm install` succeeds. Codemod output is committed. Type errors are recorded for follow-up.

---

### Unit 2: Fix Core Layout — Masthead, Page, Navigation, Sidebar

**Goal:** Fix the main application layout components that changed structurally in PF6.

**Files to modify:**
- `src/components/viewLayout/viewLayout.tsx`
- `src/components/viewLayout/viewLayoutToolbar.tsx`
- `src/components/viewLayout/viewLayoutToolbar.css`
- Related test files and snapshots in `src/components/viewLayout/__tests__/`

**Steps:**

1. **Masthead restructuring** in `viewLayout.tsx`:
   - Rename `MastheadBrand` to `MastheadLogo` (the component that holds the logo/brand image)
   - Create a new `MastheadBrand` component that wraps `MastheadLogo`
   - Ensure `MastheadToggle` and the new `MastheadBrand` are both inside `MastheadMain`
   - Import the new component names from `@patternfly/react-core`

2. **Page prop changes** in `viewLayout.tsx`:
   - Rename `header` prop to `masthead`
   - If `isTertiaryNavGrouped` is used, rename to `isHorizontalSubnavGrouped`
   - If `isTertiaryNavWidthLimited` is used, rename to `isHorizontalSubnavWidthLimited`
   - If `tertiaryNav` prop is used, rename to `horizontalSubnav`

3. **PageSidebar changes:**
   - Remove `theme` prop if present

4. **Nav changes:**
   - If `variant="tertiary"` is used, change to `variant="horizontal-subnav"`
   - Remove `theme` prop if present

5. **CSS updates** in `viewLayoutToolbar.css`:
   - Update any remaining `pf-v5-` prefixed class names to `pf-v6-`
   - Update any `--pf-v5-` CSS variable references to their PF6 equivalents
   - Review the avatar styling override for compatibility

6. **Fix the base CSS import** in `src/app.tsx`:
   - Verify `@patternfly/react-core/dist/styles/base.css` still exists in PF6 or update the import path

7. **Update tests and snapshots:**
   - Update any tests that reference old prop names or component structure
   - Delete old snapshots and regenerate: `npx jest --roots=./src -u --testPathPattern viewLayout`

**Verification:** `npm run test:types` passes for layout files. Layout-related tests pass.

---

### Unit 3: Migrate EmptyState Components

**Goal:** Replace all `EmptyStateHeader` and `EmptyStateIcon` usage with the new PF6 EmptyState API.

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

**PF6 EmptyState API:**
```tsx
// PF5 (old)
<EmptyState>
  <EmptyStateHeader titleText="Title" headingLevel="h4" icon={<EmptyStateIcon icon={CubesIcon} />} />
  <EmptyStateBody>Body text</EmptyStateBody>
  <EmptyStateFooter>
    <EmptyStateActions>...</EmptyStateActions>
  </EmptyStateFooter>
</EmptyState>

// PF6 (new)
<EmptyState titleText="Title" headingLevel="h4" icon={CubesIcon} variant={EmptyStateVariant.sm}>
  <EmptyStateBody>Body text</EmptyStateBody>
  <EmptyStateFooter>
    <EmptyStateActions>...</EmptyStateActions>
  </EmptyStateFooter>
</EmptyState>
```

**Steps:**

1. For each file:
   - Remove `EmptyStateHeader` and `EmptyStateIcon` imports
   - Move `titleText` and `headingLevel` from `EmptyStateHeader` to props on `EmptyState`
   - Move the icon component reference from `EmptyStateIcon` to the `icon` prop on `EmptyState` (pass the icon component itself, not a JSX element)
   - Remove the `<EmptyStateHeader>` and `<EmptyStateIcon>` JSX elements
   - Keep `EmptyStateBody`, `EmptyStateFooter`, `EmptyStateActions` as children

2. Update all related test files and regenerate snapshots.

**Verification:** `npm run test:types` passes. EmptyState-related tests pass. Regenerate snapshots.

---

### Unit 4: Migrate Text/TextContent to Content Component

**Goal:** Replace all `Text`, `TextContent`, `TextList`, and `TextListItem` with the new `Content` component.

**Files to modify:**
- `src/components/aboutModal/aboutModal.tsx`
- Any other files using `Text`, `TextContent`, `TextList`, `TextListItem`
- Related test files and snapshots

**PF6 Content API:**
```tsx
// PF5 (old)
<TextContent>
  <Text component="h1">Title</Text>
  <Text component="p">Paragraph</Text>
  <TextList>
    <TextListItem>Item 1</TextListItem>
  </TextList>
</TextContent>

// PF6 (new)
<Content>
  <Content component="h1">Title</Content>
  <Content component="p">Paragraph</Content>
  <Content component={ContentVariants.ul}>
    <Content component="li">Item 1</Content>
  </Content>
</Content>
```

**Steps:**

1. Replace imports:
   - Remove: `Text`, `TextContent`, `TextList`, `TextListItem`, `TextVariants`, `TextListVariants`, `TextListItemVariants`
   - Add: `Content`, `ContentVariants`

2. Replace JSX:
   - `<TextContent>` → `<Content>`
   - `<Text component="...">` → `<Content component="...">`
   - `<TextList>` → `<Content component={ContentVariants.ul}>` (or `ol` for ordered)
   - `<TextListItem>` → `<Content component="li">`

3. Update related props:
   - `isVisited` → `isVisitedLink`
   - `isPlain` → `isPlainList`

4. Update tests and regenerate snapshots.

**Verification:** `npm run test:types` passes. About modal tests pass.

---

### Unit 5: Migrate Modal Components

**Goal:** Migrate all Modal usage to the PF6 Modal API (the old Modal was deprecated in PF5; PF6 auto-promotes the "next" implementation).

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

**PF6 Modal API changes:**
The PF6 Modal is the "next" implementation that was promoted. Key differences:
- Check if the import path changed (codemods may have handled this)
- `ModalVariant` enum values may have changed
- Verify `variant`, `title`, `isOpen`, `onClose` props still work as expected
- The Modal no longer uses `appendTo` by default — it renders to `document.body`

**Steps:**

1. Verify the codemods handled the Modal promotion correctly. If imports still reference the old Modal, update them.

2. Check each Modal usage for:
   - `variant` prop values (ensure they match PF6 `ModalVariant` enum)
   - `title` prop (may need to become `titleText` or similar — check PF6 API)
   - `onClose` callback signature
   - Any `appendTo` prop usage that may need adjustment

3. For `AboutModal` (`PfAboutModal` alias in aboutModal.tsx):
   - Verify AboutModal is still exported from `@patternfly/react-core` in PF6
   - Check for any API changes specific to AboutModal

4. Update all related tests:
   - Modal rendering tests may need updates if the DOM structure changed
   - Tests querying for modal content may need `{ hidden: true }` option since default `appendTo` is now `document.body`

5. Regenerate all affected snapshots.

**Verification:** `npm run test:types` passes. All modal-related tests pass.

---

### Unit 6: Migrate Button, FormGroup, and Miscellaneous Component Changes

**Goal:** Fix remaining component API changes not handled by codemods.

**Changes to address:**

1. **Button icon changes:**
   - Icons passed as children must move to the `icon` prop
   - `isActive` → `isClicked` (if used)
   - Search all files for `<Button` usage and verify icon placement
   - Pattern:
     ```tsx
     // PF5
     <Button variant="plain"><TimesIcon /></Button>

     // PF6
     <Button variant="plain" icon={<TimesIcon />} />
     // OR for plain buttons with just an icon, the children approach may still work
     // — check PF6 docs for Button
     ```

2. **FormGroup changes:**
   - `labelIcon` → `labelHelp`
   - Search for `labelIcon` prop usage in all form components

3. **HelperTextItem changes:**
   - Remove `hasIcon` and `isDynamic` props
   - Icon now renders automatically when `variant` is non-default

4. **Checkbox/Radio changes:**
   - `isLabelBeforeButton` → `labelPosition="start"`

5. **MenuToggle changes:**
   - Icons should use `icon` prop instead of children

6. **NavItem changes:**
   - `hasNavLinkWrapper` prop removed
   - Icons passed to `icon` prop

7. **Title component:**
   - Check if `Title` component API changed; PF6 may expect different size values

8. Update all related tests and regenerate snapshots.

**Verification:** `npm run test:types` passes. All affected component tests pass.

---

### Unit 7: Migrate Vendor Code — React Table Batteries and Deprecated Select

**Goal:** Migrate the vendored react-table-batteries code, including replacing all deprecated Select components with the PF6 composable Select API.

**Files to modify:**
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/MultiselectFilterControl.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/SelectFilterControl.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/FilterToolbar.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/select-overrides.css`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/TableControls/NoDataEmptyState.tsx`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/TableControls/StateError.tsx`
- Any other vendor files with PF5 dependencies
- Related test files

**Deprecated Select → Composable Select migration:**

The deprecated `Select`, `SelectOption`, `SelectOptionObject`, and `SelectOptionProps` must be replaced with PF6's composable Select pattern:

```tsx
// PF5 deprecated Select
import { Select, SelectOption, SelectOptionObject } from '@patternfly/react-core/deprecated';

<Select
  variant={SelectVariant.single}
  onToggle={onToggle}
  onSelect={onSelect}
  isOpen={isOpen}
  selections={selected}
>
  {options.map(opt => <SelectOption key={opt} value={opt} />)}
</Select>

// PF6 composable Select
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

For multiselect (`MultiselectFilterControl.tsx`), use checkboxes within SelectOption:
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
      <SelectOption
        key={opt}
        value={opt}
        hasCheckbox
        isSelected={selected.includes(opt)}
      >
        {opt}
      </SelectOption>
    ))}
  </SelectList>
</Select>
```

**Steps:**

1. Read each vendor file to understand the current Select usage patterns.
2. Rewrite `SelectFilterControl.tsx` to use the composable Select API.
3. Rewrite `MultiselectFilterControl.tsx` to use the composable Select with checkboxes.
4. Update `FilterToolbar.tsx` to remove deprecated `SelectOptionProps` import and use the PF6 equivalent types.
5. Update or remove `select-overrides.css` — the custom scrolling CSS may need different class selectors for the PF6 Select menu.
6. Verify EmptyState changes in vendor TableControls were handled in Unit 3; if not, fix them now.
7. Update any other PF5-specific patterns in vendor code.
8. Update tests and regenerate snapshots.

**Verification:** `npm run test:types` passes. Vendor-related tests pass.

---

### Unit 8: Migrate Application Select/Dropdown Components

**Goal:** Migrate any remaining Select or Dropdown components in the main application code.

**Files to check:**
- `src/components/simpleDropdown/simpleDropdown.tsx`
- `src/components/typeAheadCheckboxes/typeaheadCheckboxes.tsx`
- `src/components/actionMenu/actionMenu.tsx`
- Any other components using Dropdown or Select patterns
- Related test files and snapshots

**Steps:**

1. **Inspect each component** to determine if it uses the old Dropdown or Select API.

2. **SimpleDropdown:** If using the old `Dropdown` API, migrate to the PF6 composable Dropdown:
   ```tsx
   import { Dropdown, DropdownItem, DropdownList, MenuToggle } from '@patternfly/react-core';
   ```

3. **TypeAheadCheckboxes:** If using deprecated Select with typeahead, migrate to PF6 Select with `typeahead` functionality using the composable pattern with a `TextInput` in the toggle.

4. **ActionMenu:** Verify Dropdown/MenuToggle usage is PF6 compatible. Check for `EllipsisVIcon` usage in `MenuToggle` — should use `icon` prop.

5. Update all related tests and regenerate snapshots.

**Verification:** `npm run test:types` passes. Component tests pass.

---

### Unit 9: CSS Cleanup, Token Resolution, and Styling Fixes

**Goal:** Resolve all remaining CSS and design token issues from the codemod output.

**Files to check:**
- `src/app.css`
- `src/components/viewLayout/viewLayoutToolbar.css`
- `src/views/sources/showSourceConnectionsModal.css`
- `src/vendor/react-table-batteries/tackle2-ui-legacy/components/FilterToolbar/select-overrides.css`
- Any `.tsx` files that reference PF CSS classes or variables inline

**Steps:**

1. **Search for placeholder tokens** (`--pf-t--temp--dev--tbd`). These were inserted by the token codemods where no 1:1 mapping exists. For each:
   - Read the comment noting the original PF5 token
   - Find the closest PF6 semantic token equivalent using the [PF6 token catalog](https://www.patternfly.org/tokens/all-patternfly-tokens)
   - Replace the placeholder with the correct PF6 token

2. **Search for remaining `pf-v5-` references** in all source files:
   ```
   grep -r "pf-v5-" ./src
   ```
   Update any that the codemods missed.

3. **Search for remaining `--pf-v5-` CSS variables:**
   ```
   grep -r "\-\-pf-v5-" ./src
   ```
   Update to PF6 equivalents.

4. **Review custom CSS overrides:**
   - `viewLayoutToolbar.css`: Check avatar styling, toolbar overrides
   - `showSourceConnectionsModal.css`: Check modal-specific styles
   - `select-overrides.css`: May need to be updated or removed after Select migration
   - `app.css`: Check global styles and animations

5. **Verify PatternFly CSS import path** in `app.tsx`:
   - Confirm `@patternfly/react-core/dist/styles/base.css` exists in PF6
   - Confirm `@patternfly/react-styles/css/components/Avatar/avatar.css` path

6. **Check for `@patternfly/react-tokens` imports** — update to `t_` prefix naming:
   ```tsx
   // PF5
   import global_spacer_sm from '@patternfly/react-tokens/dist/esm/global_spacer_sm';

   // PF6
   import { t_global_spacer_sm } from '@patternfly/react-tokens';
   ```

7. **Check breakpoint usage** — if any JavaScript/TypeScript code uses hardcoded pixel values for PF breakpoints, convert to rem (divide by 16).

**Verification:** `npm run test:types` passes. No remaining `pf-v5-` references. No placeholder tokens remain.

---

### Unit 10: Test Suite Fixes and Final Verification

**Goal:** Ensure all 33 test files pass and the application builds successfully.

**Steps:**

1. **Run the full test suite:**
   ```bash
   npm run test:ci-coverage
   ```

2. **For each failing test, diagnose and fix:**
   - **Snapshot failures:** Delete old snapshots and regenerate with `npx jest -u`
   - **Query failures:** Tests using `getByText`, `getByRole`, etc. may fail due to:
     - Changed DOM structure (e.g., Modal content in `document.body`)
     - Changed class names (v5 → v6 prefixes)
     - Changed component structure (e.g., EmptyState no longer has EmptyStateHeader element)
   - **Import failures:** Verify test files don't import removed components
   - **Type errors in tests:** Fix any `@types` mismatches

3. **Common test fixes for PF6:**
   - For Select/Dropdown menus rendered to `document.body`, use `{ hidden: true }` in queries or `screen.getByRole` which searches the whole document
   - For Modal content, similar portal-based rendering may require `baseElement` or `{ hidden: true }` queries
   - Update any assertions on PF CSS class names from `pf-v5-` to `pf-v6-`

4. **Run the type checker:**
   ```bash
   npm run test:types
   ```

5. **Run the linter:**
   ```bash
   npm run test:lint
   ```

6. **Run the full build:**
   ```bash
   npm run build
   ```

7. **Run integration tests:**
   ```bash
   npm run test:integration
   ```

8. **Verify coverage thresholds are still met** (branches: 60%, functions: 80%, lines: 80%, statements: 80%).

**Verification:** All checks pass. Application builds. Tests pass with required coverage.

---

## Summary of Units

| Unit | Scope | Key Files |
|------|-------|-----------|
| 1 | Dependencies + Codemods | `package.json`, all `src/` files (automated) |
| 2 | Core Layout (Masthead, Page, Nav, Sidebar) | `viewLayout.tsx`, `viewLayoutToolbar.tsx` + CSS |
| 3 | EmptyState Migration | 8 source files across views, components, vendor |
| 4 | Text → Content Migration | `aboutModal.tsx` + any others |
| 5 | Modal Migration | 10 source files + all related tests |
| 6 | Button, FormGroup, Misc Components | Multiple files across components/views |
| 7 | Vendor Code + Deprecated Select | 6+ vendor files |
| 8 | App Select/Dropdown Components | `simpleDropdown`, `typeAheadCheckboxes`, `actionMenu` |
| 9 | CSS Cleanup + Token Resolution | 4 CSS files + inline references |
| 10 | Test Suite + Final Verification | All 33 test files, build verification |

## Notes for the Executing Agent

- **Always read a file before modifying it.** Never assume content based on file names alone.
- **Run `npm run test:types` after each unit** to catch regressions early.
- **Regenerate snapshots** (`npx jest -u`) rather than manually editing `.snap` files.
- **The vendor code** (`src/vendor/`) is part of this codebase and should be treated as application code for migration purposes.
- **If a codemod produces incorrect output**, fix it manually rather than reverting the codemod.
- **Commit after each unit** with a descriptive message (e.g., `feat: migrate EmptyState to PF6 API`).
- **If you encounter an issue you cannot resolve**, document it clearly and move to the next unit. It can be addressed in a follow-up pass.
- **PatternFly 6 documentation:** https://www.patternfly.org/
- **PF6 component examples:** https://www.patternfly.org/components/all-components
