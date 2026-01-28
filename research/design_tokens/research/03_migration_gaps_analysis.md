# Phase 3: Migration Gaps Analysis

This document provides a categorized inventory of CSS Design Token migration gaps not covered by pf-codemods, with concrete code examples for each gap type.

---

## Executive Summary

The pf-codemods suite handles approximately 70-80% of token migration automatically. The remaining 20-30% falls into six primary gap categories requiring human intervention:

1. **Non-1:1 Token Mappings** - Tokens removed, consolidated, split, or semantically changed
2. **Color Token Selection** - All color tokens require human semantic judgment
3. **Component-Specific Tokens** - ~3000+ tokens with no v6 equivalents
4. **Custom CSS Overrides** - Application-level customizations not detected
5. **Structural Component Changes** - Components requiring refactoring, not just variable swaps
6. **Context-Dependent Decisions** - Same v5 token may map to different v6 tokens based on usage

---

## Gap Category 1: Non-1:1 Token Mappings

### 1.1 Removed Tokens (No Replacement Exists)

Some v5 tokens were intentionally removed without v6 equivalents. These represent design decisions to deprecate certain functionality.

#### Tokens Marked as SKIP

| V5 Token | V5 Value | Reason for Removal |
|----------|----------|-------------------|
| `global_BoxShadow_inset` | `inset 0 0 0.625rem 0` | Inset shadows not part of v6 design system |
| `global_arrow_width` | `0.9375rem` | Arrow components restructured |
| `global_arrow_width_lg` | `1.5625rem` | Arrow components restructured |
| `global_font_path` | Font asset path | Build system changes |
| `global_fonticon_path` | Icon font path | Icon approach changed |
| `global_target_size_MinHeight` | `44px` | Touch target sizing deprecated |
| `global_target_size_MinWidth` | `44px` | Touch target sizing deprecated |

#### Code Example: Removed Token

```css
/* V5 Pattern - Uses inset shadow */
.my-inset-panel {
  box-shadow: var(--pf-v5-global--BoxShadow--inset);
}
```

**Why pf-codemods doesn't handle it**: Token is marked "SKIP" - no replacement exists

**What developer must decide**:
- Is the inset shadow essential to the design?
- Should a custom value be used instead?
- Can the design be simplified to not need this effect?

**V6 Resolution Options**:
```css
/* Option 1: Remove the effect entirely */
.my-inset-panel {
  /* No shadow - rely on other visual boundaries */
}

/* Option 2: Use custom value if truly needed */
.my-inset-panel {
  box-shadow: inset 0 0 0.625rem 0 var(--pf-t--global--box-shadow--color--100);
}

/* Option 3: Use a standard v6 shadow instead */
.my-inset-panel {
  box-shadow: var(--pf-t--global--box-shadow--sm);
}
```

---

### 1.2 Consolidated Tokens (Many-to-One)

Multiple v5 tokens sometimes map to a single v6 token, requiring developers to verify the consolidation is appropriate for their use case.

#### Example: Font Size Consolidation

| V5 Token | V5 Value | V6 Token | V6 Value |
|----------|----------|----------|----------|
| `global_FontSize_xl` | `1.25rem` | `t_global_font_size_xl` | `1.25rem` |
| `global_FontSize_2xl` | `1.5rem` | `t_global_font_size_2xl` | `1.375rem` |
| `global_icon_FontSize_xl` | `3.375rem` | `t_global_icon_size_xl` | `2.25rem` |

Note: The v6 values are different from v5, so even "mapped" tokens may produce visual changes.

#### Code Example: Value Change in Mapping

```typescript
// V5 Pattern
import { global_FontSize_2xl } from '@patternfly/react-tokens';
// Value: 1.5rem

const headingStyle = {
  fontSize: global_FontSize_2xl.value
};
```

**Why pf-codemods partially handles it**: Codemod maps token name, but doesn't warn about value change

**What developer must decide**:
- Is 1.375rem acceptable instead of 1.5rem?
- Should explicit pixel value be used instead?
- Is this a header that needs specific sizing?

**V6 Resolution Options**:
```typescript
// Option 1: Accept the new value
import { t_global_font_size_2xl } from '@patternfly/react-tokens';
// Value is now 1.375rem

// Option 2: Use heading-specific token if this is a heading
import { t_global_font_size_heading_h2 } from '@patternfly/react-tokens';

// Option 3: Use explicit value if exact size is critical
const headingStyle = {
  fontSize: '1.5rem' // Maintains v5 sizing
};
```

---

### 1.3 Split Tokens (One-to-Many)

Some v5 tokens were split into multiple v6 tokens for different semantic contexts.

#### Example: Link Color Split

| V5 Token | V6 Options | When to Use |
|----------|------------|-------------|
| `global_link_Color` | `t_global_text_color_link_default` | Standard link text |
| | `t_global_icon_color_brand_default` | Link icons |
| | `t_global_color_brand_default` | Brand-colored elements |

#### Code Example: Split Token

```css
/* V5 Pattern - Single token for all link colors */
.my-link {
  color: var(--pf-v5-global--link--Color);
}

.my-link svg {
  fill: var(--pf-v5-global--link--Color);
}
```

**Why pf-codemods doesn't handle it**: Can't determine if this is text, icon, or brand usage

**What developer must decide**:
- Is this styling text, icons, or both?
- Should text and icons use different tokens?
- Is this a "link" context or just "brand" colored?

**V6 Resolution Options**:
```css
/* Option 1: Text-specific token */
.my-link {
  color: var(--pf-t--global--text--color--link--default);
}

/* Option 2: Icon-specific token (different shade) */
.my-link svg {
  fill: var(--pf-t--global--icon--color--brand--default);
}

/* Option 3: If both need same color, use generic brand token */
.my-link,
.my-link svg {
  color: var(--pf-t--global--color--brand--default);
  fill: var(--pf-t--global--color--brand--default);
}
```

---

### 1.4 Semantic Changes (Same Name, Different Meaning)

Some tokens kept similar names but their semantic meaning changed.

#### Example: Background Color Intent

| V5 Token | V5 Intent | V6 Token | V6 Intent |
|----------|-----------|----------|-----------|
| `global_BackgroundColor_100` | "Light background" | (no direct map) | Removed |
| `global_BackgroundColor_200` | "Darker background" | (no direct map) | Removed |
| | | `t_global_background_color_primary_default` | "Main surface" |
| | | `t_global_background_color_secondary_default` | "Secondary surface" |

#### Code Example: Semantic Change

```css
/* V5 Pattern - Numeric naming */
.panel {
  background-color: var(--pf-v5-global--BackgroundColor--100);
}

.panel-header {
  background-color: var(--pf-v5-global--BackgroundColor--200);
}
```

**Why pf-codemods doesn't handle it**: Numeric tokens don't map to semantic tokens automatically

**What developer must decide**:
- What is the semantic purpose of this background?
- Is it a "primary" or "secondary" surface?
- Is it a "floating" element (modal, dropdown)?

**V6 Resolution Options**:
```css
/* Option 1: Map to semantic primary/secondary */
.panel {
  background-color: var(--pf-t--global--background--color--primary--default);
}

.panel-header {
  background-color: var(--pf-t--global--background--color--secondary--default);
}

/* Option 2: If this is a floating element */
.panel {
  background-color: var(--pf-t--global--background--color--floating--default);
}

/* Option 3: If this needs tertiary distinction */
.panel-sidebar {
  background-color: var(--pf-t--global--background--color--tertiary--default);
}
```

---

## Gap Category 2: Color Token Selection

All color tokens (~150+) require human judgment. The codemod replaces them with `t_temp_dev_tbd` (hot pink placeholder).

### 2.1 Palette Colors

V5 exposed raw palette colors (`blue_400`, `red_200`). V6 strongly prefers semantic tokens.

#### Code Example: Palette Color Usage

```typescript
// V5 Pattern
import { global_palette_blue_400 } from '@patternfly/react-tokens';

const MyBadge = () => (
  <span style={{ backgroundColor: global_palette_blue_400.value }}>
    New
  </span>
);
```

**Why pf-codemods doesn't handle it**: Can't determine semantic intent from palette name

**What developer must decide**:
- Is "blue_400" being used for info status?
- Is this a brand indicator?
- Is this a custom styling that should match existing components?

**V6 Resolution Options**:
```typescript
// Option 1: If this is info/notification status
import { t_global_background_color_status_info_default } from '@patternfly/react-tokens';

// Option 2: If this is brand/primary indicator
import { t_global_background_color_brand_default } from '@patternfly/react-tokens';

// Option 3: If truly need palette access (rare)
import { t_color_blue_40 } from '@patternfly/react-tokens';

// Option 4: Use Label/Badge component instead of custom styling
import { Label } from '@patternfly/react-core';
const MyBadge = () => <Label color="blue">New</Label>;
```

### 2.2 Semantic Color Context

Same color may need different tokens based on whether it's for text, background, border, or icon.

#### Code Example: Multi-Context Color

```css
/* V5 Pattern - Same color for different elements */
.success-message {
  color: var(--pf-v5-global--success-color--100);
  border-color: var(--pf-v5-global--success-color--100);
  background-color: var(--pf-v5-global--success-color--100);
}

.success-message svg {
  fill: var(--pf-v5-global--success-color--100);
}
```

**Why pf-codemods doesn't handle it**: Same source token, different target tokens needed

**What developer must decide**:
- Should text, border, background, and icon all be the same shade?
- V6 semantic tokens may have intentionally different values for each context

**V6 Resolution Options**:
```css
/* Option 1: Use context-specific tokens (recommended) */
.success-message {
  color: var(--pf-t--global--text--color--status--success--default);
  border-color: var(--pf-t--global--border--color--status--success--default);
  background-color: var(--pf-t--global--background--color--status--success--default);
}

.success-message svg {
  fill: var(--pf-t--global--icon--color--status--success--default);
}

/* Note: These tokens may have different actual values for proper contrast */
```

---

## Gap Category 3: Component-Specific Tokens (~3000+)

V5 exposed internal component tokens for customization. V6 does not provide equivalent tokens.

### 3.1 Component Variable Overrides

#### Code Example: Button Customization

```css
/* V5 Pattern - Override internal button variables */
.my-custom-button {
  --pf-v5-c-button--m-primary--BackgroundColor: #5e40be;
  --pf-v5-c-button--m-primary--hover--BackgroundColor: #4a32a0;
  --pf-v5-c-button--m-primary--active--BackgroundColor: #3d2a85;
}
```

**Why pf-codemods doesn't handle it**: ~3000 component tokens have no mapping data

**What developer must decide**:
- Can the customization be achieved through v6's theming system?
- Is this customization necessary or can default styling be used?
- Does the component have new props or CSS custom properties?

**V6 Resolution Options**:
```css
/* Option 1: Use semantic tokens that components reference */
.my-custom-button {
  --pf-t--global--background--color--brand--default: #5e40be;
  --pf-t--global--background--color--brand--hover: #4a32a0;
  --pf-t--global--background--color--brand--clicked: #3d2a85;
}

/* Option 2: Override specific v6 component variables (if they exist) */
.my-custom-button.pf-v6-c-button {
  --pf-v6-c-button--m-primary--BackgroundColor: #5e40be;
}

/* Option 3: Use className and direct CSS */
.my-custom-button {
  background-color: #5e40be !important;
}
.my-custom-button:hover {
  background-color: #4a32a0 !important;
}
```

### 3.2 Component Structural Tokens

#### Code Example: Card Spacing Override

```css
/* V5 Pattern - Override card internal spacing */
.compact-card {
  --pf-v5-c-card--first-child--PaddingTop: var(--pf-v5-global--spacer--xs);
  --pf-v5-c-card__body--PaddingTop: var(--pf-v5-global--spacer--xs);
  --pf-v5-c-card__body--PaddingBottom: var(--pf-v5-global--spacer--xs);
}
```

**Why pf-codemods doesn't handle it**: Internal component structure may have changed

**What developer must decide**:
- Does the Card component still use the same internal structure?
- Are there new props for compact styling?
- Should custom CSS be replaced with component variants?

**V6 Resolution Options**:
```tsx
/* Option 1: Check for new component props */
<Card isCompact>  {/* May achieve same result */}
  ...
</Card>

/* Option 2: Use CSS with v6 token values */
.compact-card.pf-v6-c-card {
  --pf-v6-c-card--PaddingTop: var(--pf-t--global--spacer--xs);
  --pf-v6-c-card--PaddingBottom: var(--pf-t--global--spacer--xs);
}

/* Option 3: Direct CSS override */
.compact-card .pf-v6-c-card__body {
  padding: var(--pf-t--global--spacer--xs);
}
```

---

## Gap Category 4: Custom CSS Override Patterns

Application-level CSS customizations are completely invisible to codemods.

### 4.1 Direct Variable Overrides

#### Code Example: Theme Customization

```css
/* V5 Pattern - Global theme overrides */
:root {
  --pf-v5-global--primary-color--100: #5e40be;
  --pf-v5-global--primary-color--200: #4a32a0;
  --pf-v5-global--link--Color: #5e40be;
  --pf-v5-global--link--Color--hover: #4a32a0;
}
```

**Why pf-codemods doesn't handle it**: Application CSS files may not be scanned, or pattern is too broad to transform safely

**What developer must decide**:
- Which semantic tokens should receive these values?
- Should theming use v6's recommended approach?
- Are all references to these overrides accounted for?

**V6 Resolution Options**:
```css
/* Option 1: Map to equivalent v6 tokens */
:root {
  --pf-t--global--color--brand--default: #5e40be;
  --pf-t--global--color--brand--hover: #4a32a0;
  --pf-t--global--text--color--link--default: #5e40be;
  --pf-t--global--text--color--link--hover: #4a32a0;
}

/* Option 2: Override at token layer level */
:root {
  /* Override palette that flows to semantic tokens */
  --pf-t--global--palette--purple--50: #5e40be;
}
```

### 4.2 Nested Selector Overrides

#### Code Example: Scoped Component Styling

```css
/* V5 Pattern - Nested selectors targeting internals */
.my-dashboard .pf-v5-c-page__sidebar {
  --pf-v5-c-page__sidebar--Width: 200px;
  background-color: var(--pf-v5-global--BackgroundColor--dark-300);
}

.my-dashboard .pf-v5-c-page__sidebar .pf-v5-c-nav__link {
  color: var(--pf-v5-global--Color--light-100);
}
```

**Why pf-codemods doesn't handle it**: Can't safely transform nested selectors that reference component internals

**What developer must decide**:
- Has the component's internal class structure changed?
- Are there new ways to achieve this styling?
- Should styling be componentized differently?

**V6 Resolution Options**:
```css
/* Option 1: Update class names and tokens */
.my-dashboard .pf-v6-c-page__sidebar {
  --pf-v6-c-page__sidebar--Width: 200px;
  background-color: var(--pf-t--global--background--color--secondary--default);
}

.my-dashboard .pf-v6-c-page__sidebar .pf-v6-c-nav__link {
  color: var(--pf-t--global--text--color--on-dark--default);
}

/* Option 2: Use component props if available */
<PageSidebar width="200px" theme="dark">
```

### 4.3 Media Query Overrides

#### Code Example: Responsive Token Overrides

```css
/* V5 Pattern - Breakpoint-specific overrides */
@media (max-width: 576px) {
  .mobile-compact {
    --pf-v5-global--spacer--md: 0.5rem;
    --pf-v5-global--FontSize--md: 0.875rem;
  }
}
```

**Why pf-codemods doesn't handle it**: Media query context adds complexity; breakpoint values also changed (px → rem)

**What developer must decide**:
- Convert breakpoint from 576px to 36rem?
- Are these overrides still appropriate for v6's spacing/sizing?
- Should responsive behavior use different tokens?

**V6 Resolution Options**:
```css
/* Option 1: Update breakpoint and tokens */
@media (max-width: 36rem) {  /* 576px / 16 = 36rem */
  .mobile-compact {
    --pf-t--global--spacer--md: 0.5rem;
    --pf-t--global--font--size--md: 0.875rem;
  }
}

/* Option 2: Use v6 breakpoint token if available */
@media (max-width: var(--pf-t--global--breakpoint--sm)) {
  .mobile-compact {
    /* Use smaller token instead of overriding */
    padding: var(--pf-t--global--spacer--sm);
    font-size: var(--pf-t--global--font--size--sm);
  }
}
```

---

## Gap Category 5: Structural Component Changes

Some components were fundamentally restructured, not just renamed.

### 5.1 Deprecated Components

| Deprecated Component | V6 Replacement | Migration Complexity |
|---------------------|----------------|---------------------|
| `Chip` | `Label` | Low - Similar API |
| `Tile` | `Card` | Medium - Different structure |
| `ApplicationLauncher` | Custom `Menu` | High - Manual implementation |
| `ContextSelector` | Custom `Menu` | High - Manual implementation |
| `Dropdown` (legacy) | New `Dropdown` or `Menu` | Medium - API changes |
| `OptionsMenu` | `Menu` with toggle | Medium - Different pattern |
| `PageHeader` | `Masthead` + custom | High - Restructured |
| `Select` (legacy) | New `Select` or `Menu` | Medium - API changes |

#### Code Example: Chip to Label Migration

```tsx
// V5 Pattern
import { Chip, ChipGroup } from '@patternfly/react-core';

<ChipGroup>
  <Chip onClick={() => remove('item1')}>Item 1</Chip>
  <Chip onClick={() => remove('item2')}>Item 2</Chip>
</ChipGroup>
```

**Why pf-codemods partially handles it**: Can rename imports but not restructure usage

**What developer must decide**:
- Does Label have equivalent functionality?
- How should click handlers be adapted?
- Is LabelGroup the right replacement for ChipGroup?

**V6 Resolution Options**:
```tsx
// Option 1: Use Label with close button
import { Label, LabelGroup } from '@patternfly/react-core';

<LabelGroup>
  <Label onClose={() => remove('item1')}>Item 1</Label>
  <Label onClose={() => remove('item2')}>Item 2</Label>
</LabelGroup>

// Option 2: Use Label with custom click behavior
<LabelGroup>
  <Label onClick={() => handleClick('item1')}
         onClose={() => remove('item1')}>
    Item 1
  </Label>
</LabelGroup>
```

### 5.2 Internal Structure Changes

#### Code Example: EmptyState Restructuring

```tsx
// V5 Pattern
import {
  EmptyState,
  EmptyStateIcon,
  EmptyStateBody,
  EmptyStateHeader
} from '@patternfly/react-core';

<EmptyState>
  <EmptyStateHeader
    titleText="No items found"
    icon={<EmptyStateIcon icon={SearchIcon} />}
    headingLevel="h2"
  />
  <EmptyStateBody>
    Try adjusting your filters
  </EmptyStateBody>
</EmptyState>
```

**Why pf-codemods partially handles it**: Structure change requires refactoring, not just renaming

**What developer must decide**:
- How does the new EmptyState API work?
- Are EmptyStateHeader/EmptyStateIcon now internal?

**V6 Resolution Options**:
```tsx
// V6 Pattern - Uses props instead of child components
import { EmptyState, EmptyStateBody } from '@patternfly/react-core';

<EmptyState
  titleText="No items found"
  icon={SearchIcon}
  headingLevel="h2"
>
  <EmptyStateBody>
    Try adjusting your filters
  </EmptyStateBody>
</EmptyState>
```

---

## Gap Category 6: Context-Dependent Decisions

The same v5 token may require different v6 tokens depending on usage context.

### 6.1 Usage Context Matrix

| V5 Token | Context | V6 Token |
|----------|---------|----------|
| `global_Color_100` | Button text | `t_global_text_color_regular` |
| `global_Color_100` | Page background | `t_global_background_color_primary_default` |
| `global_Color_100` | Border | `t_global_border_color_default` |
| `global_primary_color_100` | Link text | `t_global_text_color_link_default` |
| `global_primary_color_100` | Icon fill | `t_global_icon_color_brand_default` |
| `global_primary_color_100` | Button bg | `t_global_background_color_brand_default` |

#### Code Example: Context-Dependent Token

```css
/* V5 Pattern - Same token, different contexts */
.my-component {
  color: var(--pf-v5-global--primary-color--100);
  border-color: var(--pf-v5-global--primary-color--100);
}

.my-component svg {
  fill: var(--pf-v5-global--primary-color--100);
}

.my-component .button {
  background-color: var(--pf-v5-global--primary-color--100);
}
```

**Why pf-codemods doesn't handle it**: Can't infer context from CSS property alone in regex-based matching

**What developer must decide**:
- What is each usage's semantic purpose?
- Should each context use different token shades?

**V6 Resolution Options**:
```css
/* V6 Pattern - Context-specific tokens */
.my-component {
  color: var(--pf-t--global--text--color--brand--default);
  border-color: var(--pf-t--global--border--color--brand--default);
}

.my-component svg {
  fill: var(--pf-t--global--icon--color--brand--default);
}

.my-component .button {
  background-color: var(--pf-t--global--background--color--brand--default);
}
```

---

## Summary: Gap Inventory

### By Frequency (Estimated Occurrence in Typical Projects)

| Gap Type | Frequency | Automation Potential |
|----------|-----------|---------------------|
| Color token selection | Very High | Low - Requires semantic judgment |
| Component-specific tokens | High | Low - No mappings exist |
| Custom CSS overrides | High | Medium - Could detect, can't transform |
| Context-dependent decisions | Medium | Low - Requires usage analysis |
| Removed tokens | Low | Medium - Could catalog and warn |
| Structural component changes | Low | Low - Requires refactoring |

### By Migration Difficulty

| Difficulty | Gap Types |
|------------|-----------|
| **Low** | Removed tokens (just delete), Simple component renames |
| **Medium** | Color token selection (guided choice), Non-1:1 mappings (options clear) |
| **High** | Component restructuring, Custom CSS overrides, Context-dependent decisions |

### By Tooling Opportunity

| Opportunity | Approach |
|-------------|----------|
| **Detection** | Identify all v5 tokens in application CSS |
| **Cataloging** | List custom overrides with their component context |
| **Suggestion** | Recommend v6 tokens based on property usage |
| **Validation** | Verify all hot pink placeholders resolved |
| **Guidance** | Provide component-specific migration documentation |

---

## Checkpoint Verification

This document provides:

1. **Categorized gap inventory**: Six primary gap categories with subcategories

2. **Concrete code examples**: Each gap type includes:
   - V5 pattern showing original code
   - Explanation of why pf-codemods doesn't handle it
   - What developer must decide
   - V6 resolution options

3. **Prioritization framework**: Gaps categorized by frequency, difficulty, and automation potential

4. **Foundation for tooling**: Clear identification of what detection, suggestion, and guidance tooling could address

---

## References

- [PatternFly Upgrade Guide](https://www.patternfly.org/get-started/upgrade)
- [All PatternFly Tokens](https://www.patternfly.org/tokens/all-patternfly-tokens)
- [pf-codemods Repository](https://github.com/patternfly/pf-codemods)
- Phase 1: Design Token Fundamentals (01_design_tokens_fundamentals.md)
- Phase 2: pf-codemods Analysis (02_pf_codemods_analysis.md)
