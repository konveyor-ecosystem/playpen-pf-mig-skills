# Phase 2: pf-codemods Analysis

## Overview

The `pf-codemods` project is a comprehensive suite of migration tools for PatternFly, consisting of four main packages:

1. **eslint-plugin-pf-codemods** - ESLint-based rules for React/TypeScript code
2. **css-vars-updater** - CSS variable migration utility
3. **class-name-updater** - CSS class name version updates
4. **shared-codemod-helpers** - Shared token lists and utilities

The official documentation states: "these rules are not designed to fix all build errors, but they can help to fix easy ones as well as point out the more complicated ones."

## Repository Structure

```
pf-codemods/
├── packages/
│   ├── eslint-plugin-pf-codemods/
│   │   └── src/rules/v6/           # 106 v6 migration rules
│   ├── css-vars-updater/           # CSS variable migration CLI
│   ├── class-name-updater/         # Class name version updater CLI
│   └── shared-codemod-helpers/
│       └── src/tokenLists/         # Token mapping data
│           ├── oldGlobalTokens.ts  # Non-color + color token maps
│           ├── oldTokens.ts        # 3000+ deprecated tokens
│           ├── tokensToPrefixWithT.ts
│           └── v6DirectionCssVars.ts
```

---

## CSS & Token-Related Codemods

### 1. tokens-update (ESLint Rule)

**Purpose**: Migrates React token imports from `@patternfly/react-tokens`

**Detection Mechanism**:
- AST-based detection via ESLint
- Processes: `ImportSpecifier`, `ImportDefaultSpecifier`, `Identifier`, `Literal` nodes
- Regex for CSS var syntax: `/var\(([^)]+)\)/`

**Transformation Logic**:

| Token Category | Handling Strategy | Example |
|----------------|-------------------|---------|
| Global non-color tokens | Direct substitution | `global_BorderRadius_lg` → `global_border_radius_large` |
| Global color tokens | Hot pink placeholder | `global_Color_100` → `t_temp_dev_tbd` |
| Component tokens | Warning only | Directs to documentation |
| Deprecated tokens | Warning only | No replacement available |

**Limitations**:
- Color tokens require manual replacement (uses placeholder)
- Component-specific tokens (~3000) have no automated mapping
- Chart tokens require manual intervention

### 2. tokensPrefixWithT (ESLint Rule)

**Purpose**: Adds `t_` prefix to tokens referencing `--pf-t` CSS variables

**Detection Mechanism**:
- Checks imports against `tokensToPrefixWithT` set
- Updates both import specifiers and usage identifiers

**Transformation**:
```typescript
// Before
import { global_font_size_lg } from '@patternfly/react-tokens';

// After
import { t_global_font_size_lg } from '@patternfly/react-tokens';
```

### 3. css-vars-updater (CLI Tool)

**Purpose**: Updates CSS variables in non-React files

**File Types Processed**: `.css`, `.scss`, `.less`, `.md`

**Detection Pattern**:
```regex
/(?<!:)(--pf-v5-[\w-]+)/g
```
The negative lookbehind `(?<!:)` prevents matching codemod comments.

**Transformation Logic** (tiered replacement):

1. **Global Non-Color Variables**: Uses `globalNonColorCssVarNamesMap` lookup
   - `--pf-v5-global--BorderRadius--lg` → `--pf-t--global--border--radius--large`

2. **Global Color Variables**: Hot pink placeholder when enabled
   - `--pf-v5-global--Color--100` → `--pf-t--temp--dev--tbd /* CODEMODS: original v5 color was:[var] */`

3. **Directional Variables**: Transforms LTR/RTL suffixes
   - `PaddingLeft` → `PaddingInlineStart`
   - Validates against `v6DirectionCssVars` set

4. **Unmapped Variables**: Simple version string replacement
   - `--pf-v5-*` → `--pf-v6-*`

**CLI Options**:
```bash
npx @patternfly/css-vars-updater ./path-to-src
npx @patternfly/css-vars-updater ./path-to-src -i  # Interactive mode
npx @patternfly/css-vars-updater ./path-to-src --fix
```

### 4. class-name-updater (CLI Tool)

**Purpose**: Updates versioned PatternFly class names

**File Types Processed**: `.css`, `.scss`, `.less`, `.ts`, `.tsx`, `.js`, `.jsx`, `.md`

**Detection Pattern**:
```regex
/(${cssVarStart})(\b|\$)pf${previousVersion}-(${bodyMatches})-/
```
Where:
- `cssVarStart`: For post-v5, requires non-dash prefix `[^-]`
- `bodyMatches`: Matches `[cul]` (component, utility, layout) for v6; includes `global|theme|color|chart` for earlier versions

**Transformation**:
```css
/* Before */
.my-class .pf-v5-c-button { }

/* After */
.my-class .pf-v6-c-button { }
```

**CLI Options**:
```bash
npx @patternfly/class-name-updater ./path-to-src --v6
npx @patternfly/class-name-updater ./path-to-src --v6 --fix
npx @patternfly/class-name-updater ./path-to-src --extensions css,scss,tsx
npx @patternfly/class-name-updater ./path-to-src --exclude file1.tsx,file2.css
```

---

## Hot Pink Fallback Behavior

When the codemods encounter color tokens without 1:1 mappings, they use a "hot pink" placeholder strategy:

### React Token (tokens-update)
```typescript
// Original v5
import { global_Color_100 } from '@patternfly/react-tokens';

// Transformed (requires manual fix)
import { t_temp_dev_tbd /* CODEMODS: original v5 token was: global_Color_100 */ } from '@patternfly/react-tokens';
```

### CSS Variable (css-vars-updater)
```css
/* Original v5 */
color: var(--pf-v5-global--Color--100);

/* Transformed (requires manual fix) */
color: var(--pf-t--temp--dev--tbd) /* CODEMODS: original v5 color was: --pf-v5-global--Color--100 */;
```

**Purpose of Hot Pink**:
1. Creates a visual indicator (bright pink color) for unmigrated tokens
2. Preserves original token name in comments for reference
3. Forces developers to manually select appropriate v6 replacement
4. Makes incomplete migrations obvious during visual testing

---

## Scenarios Requiring Manual Intervention

### Category 1: Color Token Replacement

**What codemods do**: Replace with `t_temp_dev_tbd` placeholder

**What developers must do**:
- Identify semantic intent of original color
- Select appropriate v6 token from [documentation](https://www.patternfly.org/tokens/all-patternfly-tokens)
- Consider if color is for text, background, border, icon, etc.

**Example**:
```typescript
// Codemod output - needs manual fix
t_temp_dev_tbd /* original: global_palette_blue_400 */

// Developer must choose (options vary by context)
t_global_color_brand_default        // If brand color
t_global_color_status_info_default  // If info indicator
t_color_blue_40                     // If palette access needed
```

### Category 2: Component-Specific Tokens (~3000+)

**What codemods do**: Report warning, no transformation

**What developers must do**:
- All tokens in `oldTokens` set have no v6 equivalent
- Must understand component's v6 API changes
- May need to restructure styling approach entirely

**Examples of affected tokens**:
```
c_button_m_primary_active_BackgroundColor
c_alert_m_success_icon_Color
c_card_m_selectable_raised_BoxShadow
c_drawer_m_panel_bottom_BorderTopWidth
```

### Category 3: Tokens Marked as "SKIP"

**What codemods do**: Remove usage without replacement

**What developers must do**:
- Understand why token was removed
- Find alternative styling approach
- May need different component or pattern

**Examples**:
```typescript
// Removed without replacement
global_BoxShadow_inset        // "SKIP" - no equivalent
global_target_size_MinHeight  // "SKIP" - 44px sizing removed
```

### Category 4: Structural Component Changes

**What codemods do**: Warn about deprecation, may offer partial transformation

**What developers must do**: Refactor component usage entirely

**Examples**:
- `EmptyStateHeader`/`EmptyStateIcon` → Internal to `EmptyState`, use props instead
- `MastheadBrand` → Now wraps `MastheadLogo`
- `Modal` → Previous implementation deprecated; "Next" variant is new default
- `DualListSelector` → Deprecated version moved to `/deprecated`

### Category 5: Removed Components

**What codemods do**: Warn about removal

**What developers must do**: Implement replacement or alternative

| Removed Component | Recommended Alternative |
|-------------------|------------------------|
| ApplicationLauncher | Custom Menu implementation |
| ContextSelector | Custom Menu implementation |
| Dropdown (legacy) | New Dropdown or Menu |
| OptionsMenu | Menu with toggle |
| PageHeader | Masthead + custom layout |
| Select (legacy) | New Select or Menu |
| Chip | Label component |

### Category 6: Custom CSS Overrides

**What codemods do**: Nothing - cannot detect intent

**What developers must do**:
- Custom overrides using v5 variables are not detected
- Nested selectors targeting PatternFly internals may break
- Media queries with PatternFly tokens need review

**Example patterns NOT handled**:
```css
/* Direct variable override - not detected as needing update */
.my-component {
  --pf-v5-c-button--m-primary--BackgroundColor: purple;
}

/* Nested selector override - may break in v6 */
.my-wrapper .pf-v5-c-card .pf-v5-c-card__body {
  padding: 0;
}
```

---

## Detection Patterns Summary

| Tool | Detection Method | Pattern Type |
|------|------------------|--------------|
| tokens-update | ESLint AST | ImportSpecifier, Identifier, Literal nodes |
| tokensPrefixWithT | ESLint AST | Import declarations + identifier usage |
| css-vars-updater | Regex | `/(?<!:)(--pf-v5-[\w-]+)/g` |
| class-name-updater | Regex | `/[^-](\b\|\$)pf${version}-(c\|u\|l)-/` |

---

## Token Mapping Data

The codemods rely on several key data structures in `shared-codemod-helpers`:

### globalNonColorTokensMap
Maps v5 non-color tokens to v6 equivalents:
```typescript
{
  "global_BorderRadius_lg": "global_border_radius_large",
  "global_BoxShadow_md": "global_box_shadow_md",
  "global_FontFamily_text": "global_font_family_body",
  "global_ZIndex_lg": "global_z_index_lg",
  "global_BoxShadow_inset": "SKIP",  // No replacement
  // ... ~50 mappings
}
```

### oldGlobalColorTokens (Set)
150+ color token names that get hot pink replacement:
- Background colors (dark/light/transparent variants)
- Palette colors (blue_50 through blue_700, etc.)
- Semantic colors (success, warning, danger, info)
- Link colors (default, hover, visited states)
- Icon colors (light/dark theme variations)

### oldTokens (Set)
~3000 component-specific deprecated tokens with no v6 equivalent:
- Component tokens (`c_button_*`, `c_card_*`, `c_alert_*`)
- Layout tokens
- Chart tokens

### tokensToPrefixWithT (Set)
Tokens that need `t_` prefix for v6 compatibility.

### v6DirectionCssVars (Set)
Directional CSS variables for LTR/RTL transformation validation.

---

## What pf-codemods Handles vs. Where It Stops

### Fully Automated

| Scenario | Tool | Confidence |
|----------|------|------------|
| React token imports (non-color, global) | tokens-update | High |
| Token `t_` prefix addition | tokensPrefixWithT | High |
| CSS variable version bump (v5→v6) | css-vars-updater | High |
| CSS class version bump (v5→v6) | class-name-updater | High |
| Directional property updates | css-vars-updater | Medium |
| Non-color global variable mapping | css-vars-updater | High |

### Partially Automated (Needs Review)

| Scenario | What's Automated | What's Manual |
|----------|------------------|---------------|
| Color tokens | Placeholder insertion | Selecting replacement |
| Component deprecation | Warning + sometimes structure | Refactoring usage |
| Prop renames | Many automated | Complex conditionals |
| Import path changes | Automated | Version conflicts |

### Not Handled

| Scenario | Why Not Handled |
|----------|-----------------|
| Custom CSS overrides | Cannot infer intent |
| Component-specific tokens | No 1:1 mappings exist |
| Nested selector overrides | Cannot detect safely |
| Tokens in string templates | AST limitations |
| Dynamic token usage | Runtime-only patterns |
| Removed functionality | Requires redesign |

---

## Checkpoint Verification

This document enables articulating:

1. **What pf-codemods handles**:
   - React token import transformations (ESLint AST)
   - CSS variable version updates (regex-based)
   - CSS class name version updates (regex-based)
   - Global non-color token mappings (~50 tokens)
   - Hot pink placeholders for color tokens (~150 tokens)
   - Warnings for deprecated component tokens (~3000 tokens)

2. **Where it explicitly stops**:
   - Color token selection (requires human semantic judgment)
   - Component-specific token migration (no mappings exist)
   - Custom CSS override detection (cannot infer intent)
   - Removed functionality replacement (requires redesign)
   - Structural component refactoring (partially assisted)

3. **The gap for complementary tooling**:
   - Help developers select appropriate color token replacements
   - Detect and catalog custom CSS overrides needing attention
   - Provide context-aware suggestions for component token updates
   - Identify patterns that codemods cannot safely transform
