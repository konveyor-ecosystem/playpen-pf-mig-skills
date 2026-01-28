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
