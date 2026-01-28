# PatternFly 6 Migration Research

This document contains research findings for migrating the todo-app from PatternFly 5 to PatternFly 6.

## Table of Contents
1. [Breaking Changes](#breaking-changes)
2. [Deprecated Components and Replacements](#deprecated-components-and-replacements)
3. [Component API Changes](#component-api-changes)
4. [CSS and Styling Changes](#css-and-styling-changes)
5. [Available Codemods](#available-codemods)
6. [React Version Compatibility](#react-version-compatibility)
7. [Step-by-Step Migration Process](#step-by-step-migration-process)

---

## Breaking Changes

### 1. Design Token System Overhaul
- **CSS Variables**: All `--pf-v5-*` variables changed to `--pf-t--*` format
- **React Tokens**: Syntax changed (e.g., `global_FontSize_lg` to `t_global_font_size_lg`)
- All existing CSS overrides targeting outdated styles will no longer work and must be updated

### 2. Breakpoint Unit Changes
All breakpoints converted from pixels to rem units (divide px by 16):
| Breakpoint | Old (px) | New (rem) |
|------------|----------|-----------|
| sm         | 576px    | 36rem     |
| md         | 768px    | 48rem     |
| lg         | 992px    | 62rem     |
| xl         | 1200px   | 75rem     |
| 2xl        | 1450px   | 90.625rem |

### 3. Masthead Restructuring
- `<MastheadBrand>` renamed to `<MastheadLogo>`
- `<MastheadMain>` renamed to `<MastheadBrand>`
- `<MastheadToggle>` and `<MastheadBrand>` now wrapped in `<MastheadMain>`

**Migration:**
```jsx
// PatternFly 5
<Masthead>
  <MastheadMain>
    <MastheadBrand>Logo</MastheadBrand>
  </MastheadMain>
  <MastheadContent>...</MastheadContent>
</Masthead>

// PatternFly 6
<Masthead>
  <MastheadMain>
    <MastheadBrand>
      <MastheadLogo>Logo</MastheadLogo>
    </MastheadBrand>
  </MastheadMain>
  <MastheadContent>...</MastheadContent>
</Masthead>
```

### 4. EmptyState Refactoring
- Made less composable to address styling issues
- `<EmptyStateHeader>` and `<EmptyStateIcon>` now rendered internally
- `titleText` prop is now **required** on EmptyState
- Pass `icon` prop directly to EmptyState

**Migration:**
```jsx
// PatternFly 5
<EmptyState>
  <EmptyStateHeader icon={<EmptyStateIcon icon={SearchIcon} />} titleText="No results" />
  <EmptyStateBody>...</EmptyStateBody>
</EmptyState>

// PatternFly 6
<EmptyState titleText="No results" icon={SearchIcon}>
  <EmptyStateBody>...</EmptyStateBody>
</EmptyState>
```

### 5. Button Changes
- Icon children must move to dedicated `icon` prop
- `isActive` prop renamed to `isClicked`
- `aria-disabled` now only renders when `true` (may affect tests)

### 6. Toolbar Item Changes
- `variant` prop options updated
- Replaced "chip-group" with "label-group"
- Removed "bulk-select", "overflow-menu", and "search-filter" variants

### 7. Menu Toggle Changes
- Removed `pf-m-actions` class and `SplitButtonOptions`
- Items should now be passed directly to `splitButtonItems`
- Added `isPlaceholder` prop

### 8. Charts Changes
Victory-based charts moved to "victory" directory:
```javascript
// Old
import { Area } from '@patternfly/react-charts';
// New
import { Area } from '@patternfly/react-charts/victory';
```

---

## Deprecated Components and Replacements

| Deprecated Component | Replacement |
|---------------------|-------------|
| Chip                | Label       |
| Tile                | Card (with `selectableActions`) |
| Text/TextContent/TextVariants | Content |

### Tile to Card Migration
```jsx
// PatternFly 5 Tile
<Tile title="Option" isSelected={selected} onClick={handleClick}>
  Description
</Tile>

// PatternFly 6 Card
<Card isSelectable isSelected={selected}>
  <CardHeader selectableActions={{ onChange: handleClick, isChecked: selected }}>
    <CardTitle>Option</CardTitle>
  </CardHeader>
  <CardBody>Description</CardBody>
</Card>
```

### Text to Content Migration
```jsx
// PatternFly 5
<TextContent>
  <Text component={TextVariants.h1}>Heading</Text>
  <Text component={TextVariants.p}>Paragraph</Text>
</TextContent>

// PatternFly 6
<Content component="h1">Heading</Content>
<Content component="p">Paragraph</Content>
```

---

## Component API Changes

### Components Used in todo-app

#### TextInput
- **onChange signature**: `(event: React.FormEvent<HTMLInputElement>, value: string) => void`
- Deprecated props: `isExpanded` (use `expandedProps`), `isLeftTruncated` (use `isStartTruncated`)

#### TextArea
- **onChange signature**: `(event: React.ChangeEvent<HTMLTextAreaElement>, value: string) => void`
- Requires `aria-label` or `id`

#### Checkbox
- **onChange signature**: `(event: React.FormEvent<HTMLInputElement>, checked: boolean) => void`
- Requires `id` prop

#### DatePicker
- **onChange signature**: `(event: React.FormEvent<HTMLInputElement>, value: string, date?: Date) => void`
- No required props (has sensible defaults)

#### Modal
- Structure: `ModalHeader`, `ModalBody`, `ModalFooter`
- `onClose` prop required to render close button
- Title via `title` prop on ModalHeader or as children
- `titleIconVariant` supports: success, danger, warning, info

#### Form / FormGroup
- FormGroup requires `fieldId` prop
- HelperText should be wrapped with `FormHelperText` inside FormGroup
- Validation via `validated` prop

#### EmptyState
- `titleText` prop is now **required**
- `icon` prop passed directly (not as child component)
- Removed: `EmptyStateHeader`, `EmptyStateIcon` as separate components

#### Card
- Supports `isSelectable`, `isClickable`, `isSelected`, `isClicked`
- `selectableActions` object for selection behavior
- `variant`: 'default' | 'secondary'

#### Label
- Colors: 'blue', 'teal', 'green', 'orange', 'purple', 'red', 'orangered', 'grey', 'yellow'
- Status colors: 'success', 'warning', 'danger', 'info', 'custom'
- Default color: 'grey'

#### DataList
- `DataList` requires `aria-label`
- `DataListItem` requires `id`
- `DataListCell` width: 1-5 for relative sizing
- `DataListCheck` now uses Checkbox internally

#### Dropdown
- `toggle` prop: renderer function or ReactNode with `toggleRef`
- `isOpen` and `onOpenChange` for state management
- Structure: Dropdown > DropdownList > DropdownItem

#### Masthead (see Breaking Changes above)
- Requires both `MastheadMain` and `MastheadContent`
- New `MastheadLogo` component

---

## CSS and Styling Changes

### CSS Variable Migration
| PatternFly 5 | PatternFly 6 |
|--------------|--------------|
| `--pf-v5-global-*` | `--pf-t--global-*` |
| `--pf-v5-c-*` | `--pf-v6-c-*` or tokens |

### CSS Class Migration
| PatternFly 5 | PatternFly 6 |
|--------------|--------------|
| `pf-v5-u-*` | `pf-v6-u-*` |
| `pf-v5-c-*` | `pf-v6-c-*` |
| `pf-v5-m-*` | `pf-v6-m-*` |

### Common CSS Classes in todo-app
- `pf-v5-u-p-md` -> `pf-v6-u-p-md` (padding medium)
- `pf-v5-u-mr-xs` -> `pf-v6-u-mr-xs` (margin-right extra small)

---

## Available Codemods

### Installation and Usage
```bash
# Run codemods (dry run first)
npx @patternfly/pf-codemods ./src

# Apply fixes automatically
npx @patternfly/pf-codemods ./src --fix

# Target PatternFly 6 specifically
npx @patternfly/pf-codemods ./src --v6

# For large codebases
NODE_OPTIONS=--max-old-space-size=4096 npx @patternfly/pf-codemods ./src --v6
```

### Available Codemod Tools
1. **Main codemod**: `npx @patternfly/pf-codemods@latest <path> --v6`
2. **class-name-updater**: Replaces `pf-v5` prefixes with `pf-v6`
3. **tokens-update**: Updates global CSS variables and React tokens
4. **css-vars-updater**: Updates CSS variables in .css/.scss files

### Key Transformations
- Accordion: Relocates `isExpanded` from AccordionToggle to AccordionItem
- Avatar: `border` prop -> `isBordered`
- Button: `isActive` -> `isClicked`, icon children -> `icon` prop
- Card: Removes obsolete props (`isSelectableRaised`, `isDisabledRaised`, etc.)

### Post-Codemod Cleanup
```bash
npx @patternfly/pf-codemods ./src --only data-codemods-cleanup
```

---

## React Version Compatibility

- **Supported**: React 17, 18, and 19
- **React 19**: Fully supported as of v6.3 release
- No changes needed for React 18 createRoot usage

---

## Step-by-Step Migration Process

### Phase 1: Preparation
1. Research and document (this document)
2. Analyze current dependencies
3. Create component usage inventory
4. Identify CSS variable and class references

### Phase 2: Dependency Updates
1. Update all `@patternfly/*` packages to v6
2. Run `npm install`
3. Document any peer dependency warnings

### Phase 3: Automated Migration
1. Run codemods: `npx @patternfly/pf-codemods ./src --v6 --fix`
2. Run class-name-updater for CSS classes
3. Run css-vars-updater for SCSS files
4. Commit codemod changes separately for traceability

### Phase 4: Manual Updates
1. Update Masthead structure (component renaming)
2. Update EmptyState (titleText prop, remove header components)
3. Replace Tile with Card
4. Replace Text/TextContent with Content
5. Update onChange signatures where needed
6. Update CSS variables from `--pf-v5-*` to `--pf-t--*`
7. Update CSS classes from `pf-v5-*` to `pf-v6-*`

### Phase 5: Verification
1. Run TypeScript compilation
2. Run linter
3. Run E2E tests
4. Manual browser verification

---

## Files to Modify in todo-app

Based on the PRD, these files need updates:
- `src/main.tsx` - Entry point, CSS imports
- `src/components/layout/AppNav.tsx` - Masthead components
- `src/components/dashboard/Dashboard.tsx` - Card, Grid, DataList, Form
- `src/components/todos/TodoList.tsx` - Table, Dropdown, EmptyState, Checkbox, Label
- `src/components/todos/TodoModal.tsx` - Modal, Form, DatePicker, Tile
- `src/components/todos/DeleteConfirmationModal.tsx` - Modal, Button
- All SCSS files with `--pf-v5-*` variables
- All TSX files with `pf-v5-*` class references

---

## Dependency Analysis

### PatternFly Package Versions

#### Before Migration (PF5)
| Package | Version |
|---------|---------|
| @patternfly/patternfly | 5.0.2 |
| @patternfly/react-core | 5.2.1 |
| @patternfly/react-icons | 5.2.1 |
| @patternfly/react-table | 5.2.1 |

#### After Migration (PF6) - US-003 Completed
| Package | Version |
|---------|---------|
| @patternfly/patternfly | 6.4.0 |
| @patternfly/react-core | 6.4.1 |
| @patternfly/react-icons | 6.4.0 |
| @patternfly/react-table | 6.4.1 |

**Peer Dependency Warnings**: None. All dependencies resolved cleanly.

### React Compatibility

| Package | Current Version | PF6 Compatibility |
|---------|-----------------|-------------------|
| react | ^18.0.0 | ✅ Supported (PF6 supports React 17, 18, 19) |
| react-dom | ^18.0.0 | ✅ Supported |

**Note**: React 18 createRoot usage is fully compatible with PatternFly 6.

### Other Dependencies (No changes required)

- react-router-dom: ^6.0.0
- vite: ^5.0.0
- typescript: ^5.0.0
- sass: ^1.69.0

---

## Component Inventory

### @patternfly/react-core Components by File

#### src/components/layout/AppNav.tsx
| Component | Migration Notes |
|-----------|-----------------|
| Masthead | Restructured in PF6 |
| MastheadMain | Renamed (was container, now wrapper for MastheadBrand) |
| MastheadBrand | Renamed to MastheadLogo in PF6 |
| MastheadContent | No changes |
| Toolbar | No significant changes |
| ToolbarContent | No significant changes |
| ToolbarItem | `variant` prop options updated |
| Button | Icon children -> `icon` prop |
| Text | **DEPRECATED** - Replace with Content |
| TextContent | **DEPRECATED** - Replace with Content |
| TextVariants | **DEPRECATED** - Use component prop on Content |

#### src/components/dashboard/Dashboard.tsx
| Component | Migration Notes |
|-----------|-----------------|
| PageSection | `variant` prop may change |
| Grid | No significant changes |
| GridItem | No significant changes |
| Card | New selectableActions API |
| CardTitle | No significant changes |
| CardBody | No significant changes |
| Button | Icon children -> `icon` prop |
| Text | **DEPRECATED** - Replace with Content |
| TextContent | **DEPRECATED** - Replace with Content |
| TextVariants | **DEPRECATED** |
| Flex | No significant changes |
| FlexItem | No significant changes |
| DataList | Requires `aria-label` |
| DataListItem | Requires `id` prop |
| DataListItemRow | No significant changes |
| DataListItemCells | No significant changes |
| DataListCell | No significant changes |
| Checkbox | onChange signature changed |
| Label | Color options updated |
| Form | No significant changes |
| FormGroup | Requires `fieldId` prop |
| TextInput | onChange signature changed |
| ActionGroup | No significant changes |

#### src/components/todos/TodoList.tsx
| Component | Migration Notes |
|-----------|-----------------|
| PageSection | `variant` prop may change |
| Button | Icon children -> `icon` prop |
| Text | **DEPRECATED** - Replace with Content |
| TextContent | **DEPRECATED** |
| TextVariants | **DEPRECATED** |
| Flex | No significant changes |
| FlexItem | No significant changes |
| Dropdown | toggle pattern may change |
| MenuToggle | SplitButtonOptions removed |
| DropdownList | No significant changes |
| DropdownItem | No significant changes |
| Switch | No significant changes |
| Checkbox | onChange signature changed |
| Label | Color options updated |
| EmptyState | **MAJOR**: titleText required, icon prop, no more EmptyStateHeader/EmptyStateIcon |
| EmptyStateBody | No significant changes |

#### src/components/todos/TodoModal.tsx
| Component | Migration Notes |
|-----------|-----------------|
| Modal | Structure changed: ModalHeader, ModalBody, ModalFooter |
| Button | Icon children -> `icon` prop |
| Text | **DEPRECATED** - Replace with Content |
| TextContent | **DEPRECATED** |
| TextVariants | **DEPRECATED** |
| Form | No significant changes |
| FormGroup | Requires `fieldId` prop |
| TextInput | onChange signature changed |
| TextArea | onChange signature changed, requires aria-label/id |
| DatePicker | onChange signature changed |
| Tile | **DEPRECATED** - Replace with Card + selectableActions |
| Flex | No significant changes |
| FlexItem | No significant changes |
| FormHelperText | No significant changes |
| HelperText | No significant changes |
| HelperTextItem | No significant changes |
| ActionGroup | No significant changes |

#### src/components/todos/DeleteConfirmationModal.tsx
| Component | Migration Notes |
|-----------|-----------------|
| Modal | Structure changed: ModalHeader, ModalBody, ModalFooter |
| Button | variant="danger" - no changes expected |
| Text | **DEPRECATED** - Replace with Content |
| TextContent | **DEPRECATED** |
| TextVariants | **DEPRECATED** |

### @patternfly/react-table Components

#### src/components/todos/TodoList.tsx
| Component | Migration Notes |
|-----------|-----------------|
| Table | No significant changes |
| Thead | No significant changes |
| Tbody | No significant changes |
| Tr | No significant changes |
| Th | sort prop structure may change |
| Td | No significant changes |

### @patternfly/react-icons

#### src/components/todos/TodoList.tsx
| Icon | Migration Notes |
|------|-----------------|
| EditIcon | No changes |
| TrashIcon | No changes |
| TimesIcon | No changes |

#### src/components/dashboard/Dashboard.tsx
| Icon | Migration Notes |
|------|-----------------|
| PlusCircleIcon | No changes |

---

## CSS Variable Inventory

### Files with `--pf-v5-*` CSS Variables

#### src/App.scss (3 references)
- `--pf-v5-global--BackgroundColor--100` (x2)
- `--pf-v5-global--spacer--sm`

#### src/index.css (4 references)
- `--pf-v5-global--FontFamily--text`
- `--pf-v5-global--FontSize--md`
- `--pf-v5-global--Color--100`
- `--pf-v5-global--BackgroundColor--100`

#### src/components/layout/AppNav.scss (6 references)
- `--pf-v5-global--BackgroundColor--dark-100`
- `--pf-v5-global--BorderWidth--sm`
- `--pf-v5-global--BorderColor--100`
- `--pf-v5-global--Color--light-100`
- `--pf-v5-global--FontSize--xl`
- `--pf-v5-global--FontWeight--bold`
- `--pf-v5-global--FontSize--lg`

#### src/components/dashboard/Dashboard.scss (12 references)
- `--pf-v5-global--spacer--md`
- `--pf-v5-global--BorderWidth--sm`
- `--pf-v5-global--BorderColor--100`
- `--pf-v5-global--FontSize--4xl`
- `--pf-v5-global--FontWeight--bold`
- `--pf-v5-global--spacer--lg`
- `--pf-v5-global--BorderWidth--lg`
- `--pf-v5-global--danger-color--100`
- `--pf-v5-global--spacer--sm`

#### src/components/dashboard/Dashboard.tsx (5 inline style references)
- `--pf-v5-global--FontSize--4xl` (x3)
- `--pf-v5-global--danger-color--100`
- `--pf-v5-global--success-color--100`
- `--pf-v5-global--spacer--md`

#### src/components/todos/TodoList.scss (10 references)
- `--pf-v5-global--spacer--md`
- `--pf-v5-global--BackgroundColor--light-100`
- `--pf-v5-global--BorderWidth--sm`
- `--pf-v5-global--BorderColor--100`
- `--pf-v5-global--breakpoint--md`
- `--pf-v5-global--spacer--sm`
- `--pf-v5-global--BorderWidth--lg`
- `--pf-v5-global--danger-color--100`

#### src/components/todos/TodoList.tsx (1 inline style reference)
- `--pf-v5-global--spacer--sm`

#### src/components/todos/TodoModal.scss (7 references)
- `--pf-v5-global--spacer--md`
- `--pf-v5-global--BorderWidth--sm`
- `--pf-v5-global--BorderColor--100`
- `--pf-v5-global--active-color--100`

#### src/components/todos/TodoModal.tsx (1 inline style reference)
- `--pf-v5-global--BorderWidth--sm`

#### src/components/todos/DeleteConfirmationModal.scss (6 references)
- `--pf-v5-global--spacer--md`
- `--pf-v5-global--BorderWidth--sm`
- `--pf-v5-global--BorderColor--100`
- `--pf-v5-global--spacer--sm`

#### src/utils/colorUtils.ts (6 references)
- `--pf-v5-global--danger-color--100`
- `--pf-v5-global--warning-color--100`
- `--pf-v5-global--info-color--100`
- `--pf-v5-global--success-color--100`
- `--pf-v5-global--purple--100`
- `--pf-v5-global--Color--200`

---

## CSS Class Inventory

### Files with `pf-v5-*` CSS Classes

#### src/App.scss
- `.pf-v5-c-page` (component class)

#### src/components/todos/TodoList.tsx (inline className)
- `pf-v5-u-p-md` (utility: padding medium)
- `pf-v5-u-mr-xs` (utility: margin-right extra small)

#### src/components/todos/TodoList.scss
- `.pf-v5-c-flex` (component class)

#### src/components/todos/TodoModal.scss
- `.pf-v5-c-tile` (component class - will be removed when Tile replaced)

---

## Migration Priority Summary

### High Priority (Breaking Changes)
1. **Masthead restructuring** - AppNav.tsx
2. **EmptyState API changes** - TodoList.tsx
3. **Tile → Card replacement** - TodoModal.tsx
4. **Text/TextContent deprecation** - All 5 component files

### Medium Priority (API Changes)
1. **onChange signature updates** - TextInput, TextArea, Checkbox, DatePicker
2. **Modal structure changes** - TodoModal.tsx, DeleteConfirmationModal.tsx
3. **Button icon prop** - Multiple files

### Lower Priority (CSS Updates)
1. **CSS Variables** - 55+ references across 10 files
2. **CSS Classes** - 5 references across 4 files
