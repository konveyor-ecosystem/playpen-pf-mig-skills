# PRD: PatternFly 5 to 6 Migration - Todo App

## Introduction

Migrate the todo-app application from PatternFly 5 to PatternFly 6. This migration involves researching the upgrade process, updating dependencies, modifying component APIs and imports, updating CSS variable references, and verifying functionality through Playwright e2e tests. The application currently uses PatternFly 5.2.1 for react-core/react-icons/react-table and 5.0.2 for base CSS.

**Current PatternFly Dependencies:**
- `@patternfly/patternfly`: 5.0.2
- `@patternfly/react-core`: 5.2.1
- `@patternfly/react-icons`: 5.2.1
- `@patternfly/react-table`: 5.2.1

**Source Files with PatternFly Components:**
- `src/main.tsx` - Entry point, CSS imports
- `src/components/layout/AppNav.tsx` - Masthead, Toolbar
- `src/components/dashboard/Dashboard.tsx` - Card, Grid, DataList, Form
- `src/components/todos/TodoList.tsx` - Table, Dropdown, PageSection
- `src/components/todos/TodoModal.tsx` - Modal, Form, DatePicker, Tile
- `src/components/todos/DeleteConfirmationModal.tsx` - Modal, Button

## Goals

- Upgrade all PatternFly dependencies from v5 to v6
- Update all component APIs to match PatternFly 6 specifications
- Update CSS variable references from `--pf-v5-*` to PatternFly 6 equivalents
- Update CSS class references from `pf-v5-*` to PatternFly 6 equivalents
- Maintain all existing functionality (CRUD operations, filtering, sorting)
- Pass all existing Playwright e2e tests
- Keep the application buildable and type-safe throughout migration

## User Stories

### US-001: Research PatternFly 6 Upgrade Documentation
**Description:** As a developer, I need to research the official PatternFly 6 upgrade guide to understand all breaking changes and migration requirements.

**Acceptance Criteria:**
- [ ] Fetch content from https://www.patternfly.org/get-started/upgrade
- [ ] Document all breaking changes between PatternFly 5 and 6
- [ ] Identify deprecated components and their replacements
- [ ] Document API changes for components used in todo-app
- [ ] Document CSS/styling changes and class name updates
- [ ] Identify available codemods or migration tools
- [ ] Create `patternfly-6-research.md` with findings in project root

---

### US-002: Analyze Todo-App Dependencies
**Description:** As a developer, I need to analyze the current dependencies to understand the migration scope.

**Acceptance Criteria:**
- [ ] Document current PatternFly package versions from package.json
- [ ] List all PatternFly-related dependencies
- [ ] Verify React version compatibility with PatternFly 6
- [ ] Document build tool configuration (Vite)
- [ ] Add dependency analysis to `patternfly-6-research.md`

---

### US-003: Map PatternFly Component Usage
**Description:** As a developer, I need to create an inventory of all PatternFly components used in the application.

**Acceptance Criteria:**
- [ ] Search all imports from `@patternfly/react-core`
- [ ] Search all imports from `@patternfly/react-icons`
- [ ] Search all imports from `@patternfly/react-table`
- [ ] Create component usage matrix with file paths
- [ ] Document which props are used for each component
- [ ] Add component inventory to `patternfly-6-research.md`

---

### US-004: Document CSS Variable and Class Usage
**Description:** As a developer, I need to identify all PatternFly CSS variables and classes used in the application.

**Acceptance Criteria:**
- [ ] Search for `--pf-v5-` CSS variable references
- [ ] Search for `pf-v5-` CSS class references
- [ ] Document findings with file paths and line numbers
- [ ] Add CSS usage inventory to `patternfly-6-research.md`

---

### US-005: Update PatternFly Dependencies in package.json
**Description:** As a developer, I need to update all PatternFly packages to version 6.

**Acceptance Criteria:**
- [ ] Update `@patternfly/patternfly` to latest v6
- [ ] Update `@patternfly/react-core` to latest v6
- [ ] Update `@patternfly/react-icons` to latest v6
- [ ] Update `@patternfly/react-table` to latest v6
- [ ] Run `npm install` successfully
- [ ] Document any peer dependency warnings

---

### US-006: Run PatternFly 6 Codemods
**Description:** As a developer, I need to run any available PatternFly 6 codemods to automate as many migrations as possible.

**Acceptance Criteria:**
- [ ] Identify available codemods from research
- [ ] Run codemods on the codebase if available
- [ ] Document which changes were made automatically
- [ ] Document which changes require manual intervention
- [ ] Commit codemod changes separately for traceability

---

### US-007: Update main.tsx Entry Point
**Description:** As a developer, I need to update the main entry point file for PatternFly 6 compatibility.

**File:** `todo-app/src/main.tsx`

**Acceptance Criteria:**
- [ ] Update PatternFly CSS import paths if changed in v6
- [ ] Verify React 18 createRoot usage is compatible
- [ ] TypeScript compiles without errors (`npm run build`)
- [ ] Lint passes (`npm run lint`)

---

### US-008: Update AppNav.tsx Masthead Components
**Description:** As a developer, I need to update the navigation component's Masthead, Toolbar, and related components for PatternFly 6.

**File:** `todo-app/src/components/layout/AppNav.tsx`

**Components to update:**
- Masthead, MastheadMain, MastheadBrand, MastheadContent
- Toolbar, ToolbarContent, ToolbarItem
- Button, Text, TextContent, TextVariants

**Acceptance Criteria:**
- [ ] Update Masthead component API per PF6 changes
- [ ] Update Toolbar component API per PF6 changes
- [ ] Update Button component props if changed
- [ ] Update Text/TextContent/TextVariants if changed
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify navigation works via Playwright: `npm run test:e2e -- e2e/tests/navigation.spec.ts`

---

### US-009: Update Dashboard.tsx Card and Grid Components
**Description:** As a developer, I need to update the Card and Grid layout components in the Dashboard.

**File:** `todo-app/src/components/dashboard/Dashboard.tsx`

**Components to update:**
- Card, CardTitle, CardBody
- Grid, GridItem
- PageSection

**Acceptance Criteria:**
- [ ] Update Card component API per PF6 changes
- [ ] Update Grid/GridItem component API per PF6 changes
- [ ] Update PageSection variant prop if changed
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify dashboard statistics display via Playwright: `npm run test:e2e -- e2e/tests/dashboard/statistics.spec.ts`

---

### US-010: Update Dashboard.tsx DataList Components
**Description:** As a developer, I need to update the DataList components used for displaying overdue todos.

**File:** `todo-app/src/components/dashboard/Dashboard.tsx`

**Components to update:**
- DataList, DataListItem, DataListItemRow
- DataListItemCells, DataListCell
- Checkbox, Label

**Acceptance Criteria:**
- [ ] Update DataList component API per PF6 changes
- [ ] Update DataListCell width prop if changed
- [ ] Update Checkbox component API per PF6 changes
- [ ] Update Label component API per PF6 changes
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify overdue list displays via Playwright: `npm run test:e2e -- e2e/tests/dashboard/overdue-list.spec.ts`

---

### US-011: Update Dashboard.tsx Form Components
**Description:** As a developer, I need to update the quick create form components in the Dashboard.

**File:** `todo-app/src/components/dashboard/Dashboard.tsx`

**Components to update:**
- Form, FormGroup, TextInput, ActionGroup
- Button, Flex, FlexItem

**Acceptance Criteria:**
- [ ] Update Form/FormGroup component API per PF6 changes
- [ ] Update TextInput onChange signature if changed
- [ ] Update ActionGroup component API per PF6 changes
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify quick create works via Playwright: `npm run test:e2e -- e2e/tests/dashboard/quick-create.spec.ts`

---

### US-012: Update TodoList.tsx Table Components
**Description:** As a developer, I need to update the Table components from @patternfly/react-table.

**File:** `todo-app/src/components/todos/TodoList.tsx`

**Components to update:**
- Table, Thead, Tbody, Tr, Th, Td (from @patternfly/react-table)
- Sort functionality props

**Acceptance Criteria:**
- [ ] Update Table component API per PF6 changes
- [ ] Update Th sort prop structure if changed
- [ ] Update Td component API per PF6 changes
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify table displays and sorts via Playwright: `npm run test:e2e -- e2e/tests/todo-list/sorting.spec.ts`

---

### US-013: Update TodoList.tsx Dropdown and Filter Components
**Description:** As a developer, I need to update the Dropdown, MenuToggle, and filter-related components.

**File:** `todo-app/src/components/todos/TodoList.tsx`

**Components to update:**
- Dropdown, MenuToggle, DropdownList, DropdownItem
- Switch

**Acceptance Criteria:**
- [ ] Update Dropdown component API per PF6 changes
- [ ] Update MenuToggle toggle prop pattern if changed
- [ ] Update DropdownItem onClick if changed
- [ ] Update Switch component API per PF6 changes
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify filtering works via Playwright: `npm run test:e2e -- e2e/tests/todo-list/filtering.spec.ts`

---

### US-014: Update TodoList.tsx Remaining Components
**Description:** As a developer, I need to update the remaining components in TodoList.

**File:** `todo-app/src/components/todos/TodoList.tsx`

**Components to update:**
- PageSection, Button, Text, TextContent, TextVariants
- Flex, FlexItem, Checkbox, Label
- EmptyState, EmptyStateBody

**Acceptance Criteria:**
- [ ] Update PageSection variant prop if changed
- [ ] Update EmptyState component API per PF6 changes
- [ ] Update Checkbox onChange signature if changed
- [ ] Update Label color prop if changed
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify CRUD operations via Playwright: `npm run test:e2e -- e2e/tests/todo-list/crud-operations.spec.ts`

---

### US-015: Update TodoModal.tsx Form Components
**Description:** As a developer, I need to update the form components in the TodoModal.

**File:** `todo-app/src/components/todos/TodoModal.tsx`

**Components to update:**
- Form, FormGroup, TextInput, TextArea
- FormHelperText, HelperText, HelperTextItem
- ActionGroup

**Acceptance Criteria:**
- [ ] Update Form/FormGroup component API per PF6 changes
- [ ] Update TextInput/TextArea onChange signatures if changed
- [ ] Update FormHelperText pattern if changed
- [ ] Update validated prop values if changed
- [ ] TypeScript compiles without errors
- [ ] Lint passes

---

### US-016: Update TodoModal.tsx Modal, DatePicker, and Tile Components
**Description:** As a developer, I need to update the Modal, DatePicker, and Tile components in TodoModal.

**File:** `todo-app/src/components/todos/TodoModal.tsx`

**Components to update:**
- Modal
- DatePicker
- Tile
- Button, Text, TextContent, TextVariants, Flex, FlexItem

**Acceptance Criteria:**
- [ ] Update Modal component API per PF6 changes (header/footer patterns)
- [ ] Update DatePicker onChange signature if changed
- [ ] Update Tile component API per PF6 changes
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify create modal works via Playwright: `npm run test:e2e -- e2e/tests/modal/create-modal.spec.ts`
- [ ] Verify edit modal works via Playwright: `npm run test:e2e -- e2e/tests/modal/edit-modal.spec.ts`

---

### US-017: Update DeleteConfirmationModal.tsx
**Description:** As a developer, I need to update the delete confirmation modal component.

**File:** `todo-app/src/components/todos/DeleteConfirmationModal.tsx`

**Components to update:**
- Modal
- Button, Text, TextContent, TextVariants

**Acceptance Criteria:**
- [ ] Update Modal component API per PF6 changes
- [ ] Update Button variant="danger" if changed
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Verify delete modal works via Playwright: `npm run test:e2e -- e2e/tests/modal/delete-modal.spec.ts`

---

### US-018: Update CSS Variable References
**Description:** As a developer, I need to update all CSS variable references from PF5 to PF6 format.

**Files to check:**
- `todo-app/src/App.scss`
- `todo-app/src/components/**/*.scss`
- All inline styles in TSX files

**Acceptance Criteria:**
- [ ] Search for `--pf-v5-global--` in all files
- [ ] Replace with PatternFly 6 equivalent variable names
- [ ] Update inline styles in Dashboard.tsx
- [ ] Update inline styles in TodoList.tsx
- [ ] Update inline styles in TodoModal.tsx
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Application builds successfully (`npm run build`)

---

### US-019: Update CSS Class References
**Description:** As a developer, I need to update all CSS class references from PF5 to PF6 format.

**Files to check:**
- All TSX files with `pf-v5-` class references
- All SCSS files with PF5 class overrides

**Acceptance Criteria:**
- [ ] Search for `pf-v5-` in all files
- [ ] Replace with PatternFly 6 equivalent class names
- [ ] Update TodoList.tsx class references (e.g., `pf-v5-u-p-md`, `pf-v5-u-mr-xs`)
- [ ] TypeScript compiles without errors
- [ ] Lint passes
- [ ] Application builds successfully

---

### US-020: Fix Remaining TypeScript Errors
**Description:** As a developer, I need to resolve any remaining TypeScript errors after component migrations.

**Acceptance Criteria:**
- [ ] Run `npm run build` and capture all TypeScript errors
- [ ] Fix each error in order of dependency
- [ ] Ensure no type assertions are used to suppress real issues
- [ ] All files compile without errors
- [ ] Lint passes on all files
- [ ] Build completes successfully

---

### US-021: Run Full E2E Test Suite and Verify Application
**Description:** As a developer, I need to verify all functionality works correctly after migration by running the complete Playwright e2e test suite.

**Acceptance Criteria:**
- [ ] Run `npm run test:e2e` - all tests pass
- [ ] Verify navigation between Dashboard and Todo List works
- [ ] Verify CRUD operations work (create, read, update, delete todos)
- [ ] Verify filtering by priority, color, and overdue status works
- [ ] Verify sorting by title and date works
- [ ] Verify mark as done functionality works
- [ ] Verify statistics on dashboard update correctly
- [ ] Document any test failures and their resolutions

---

## Functional Requirements

- FR-1: All PatternFly dependencies must be updated to version 6.x
- FR-2: All component imports must use PatternFly 6 module paths
- FR-3: All component APIs must match PatternFly 6 specifications
- FR-4: All CSS variables must use PatternFly 6 naming conventions
- FR-5: All CSS utility classes must use PatternFly 6 naming conventions
- FR-6: The application must build without TypeScript errors
- FR-7: The application must pass ESLint without errors
- FR-8: All existing Playwright e2e tests must pass
- FR-9: The UI must maintain visual consistency with the PF5 version

## Non-Goals

- No new features will be added during migration
- No refactoring beyond what is required for PF6 compatibility
- No updates to non-PatternFly dependencies (React, Vite, etc.)
- No changes to application logic or state management
- No changes to routing structure
- No updates to Playwright test framework itself

## Technical Considerations

- **Build Tool:** Vite 5.x - check for any PF6-specific Vite configuration
- **React Version:** React 18.x - verify PF6 compatibility
- **TypeScript:** Strict mode enabled - all changes must be type-safe
- **E2E Tests:** Playwright tests rely on specific selectors - update if component structure changes
- **CSS Architecture:** SCSS with PatternFly variables - maintain separation of concerns

## Success Metrics

- All 21 user stories completed with `passes: true`
- Zero TypeScript compilation errors
- Zero ESLint errors
- 100% of existing Playwright e2e tests passing
- Application builds successfully with `npm run build`
- Application runs correctly with `npm run dev`

## Open Questions

- What version of PatternFly 6 should be targeted? (latest stable recommended)
- Are there any PatternFly 6 components that have been completely removed with no replacement?
- Do any PatternFly 6 changes require React 19 or other dependency updates?
- Are there breaking changes to the react-table package that affect sorting/filtering?
