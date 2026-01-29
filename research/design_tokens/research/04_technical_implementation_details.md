# Phase 4: Technical Implementation Details

This document provides implementation-ready technical specifications for building detection and suggestion tooling to complement pf-codemods in the PatternFly 5 to 6 migration.

---

## 1. Token Mapping Documentation

### 1.1 V5 → V6 Token Mappings (Where Mappings Exist)

The pf-codemods repository contains authoritative mapping data in `packages/shared-codemod-helpers/src/tokenLists/`.

#### Global Non-Color Token Mappings (~64 mappings)

These tokens have direct 1:1 mappings and can be automatically transformed.

| Category | V5 Token | V6 Token |
|----------|----------|----------|
| **Border Radius** | `global_BorderRadius_lg` | `global_border_radius_large` |
| | `global_BorderRadius_sm` | `global_border_radius_small` |
| **Border Width** | `global_BorderWidth_lg` | `global_border_width_extra_strong` |
| | `global_BorderWidth_xl` | `global_border_width_extra_strong` |
| | `global_BorderWidth_md` | `global_border_width_strong` |
| | `global_BorderWidth_sm` | `global_border_width_regular` |
| **Box Shadow** | `global_BoxShadow_sm` | `global_box_shadow_sm` |
| | `global_BoxShadow_md` | `global_box_shadow_md` |
| | `global_BoxShadow_lg` | `global_box_shadow_lg` |
| | `global_BoxShadow_xl` | `global_box_shadow_lg` |
| **Typography** | `global_FontFamily_text` | `global_font_family_body` |
| | `global_FontFamily_heading` | `global_font_family_heading` |
| | `global_FontFamily_monospace` | `global_font_family_mono` |
| | `global_FontWeight_bold` | `global_font_weight_heading_bold` |
| | `global_FontWeight_normal` | `global_font_weight_body_default` |
| | `global_LineHeight_md` | `global_font_line_height_body` |
| | `global_LineHeight_sm` | `global_font_line_height_heading` |
| **Font Sizes** | `global_FontSize_xs` | `global_font_size_xs` |
| | `global_FontSize_sm` | `global_font_size_sm` |
| | `global_FontSize_md` | `global_font_size_md` |
| | `global_FontSize_lg` | `global_font_size_lg` |
| | `global_FontSize_xl` | `global_font_size_xl` |
| | `global_FontSize_2xl` | `global_font_size_2xl` |
| | `global_FontSize_3xl` | `global_font_size_3xl` |
| | `global_FontSize_4xl` | `global_font_size_4xl` |
| **Spacing** | `global_spacer_xs` | `global_spacer_xs` |
| | `global_spacer_sm` | `global_spacer_sm` |
| | `global_spacer_md` | `global_spacer_md` |
| | `global_spacer_lg` | `global_spacer_lg` |
| | `global_spacer_xl` | `global_spacer_xl` |
| | `global_spacer_2xl` | `global_spacer_2xl` |
| | `global_spacer_3xl` | `global_spacer_3xl` |
| | `global_spacer_4xl` | `global_spacer_4xl` |
| | `global_gutter` | `global_spacer_gutter_default` |
| | `global_gutter_md` | `global_spacer_gutter_default` |
| **Icon Sizes** | `global_icon_FontSize_sm` | `global_icon_size_xs` |
| | `global_icon_FontSize_md` | `global_icon_size_sm` |
| | `global_icon_FontSize_lg` | `global_icon_size_2xl` |
| | `global_icon_FontSize_xl` | `global_icon_size_4xl` |
| **Z-Index** | `global_ZIndex_xs` | `global_z_index_xs` |
| | `global_ZIndex_sm` | `global_z_index_sm` |
| | `global_ZIndex_md` | `global_z_index_md` |
| | `global_ZIndex_lg` | `global_z_index_lg` |
| | `global_ZIndex_xl` | `global_z_index_xl` |
| | `global_ZIndex_2xl` | `global_z_index_2xl` |
| **Transitions** | `global_Transition` | `global_transition` |
| | `global_TransitionDuration` | `global_motion_duration` |

#### CSS Variable Name Mappings

| V5 CSS Variable | V6 CSS Variable |
|-----------------|-----------------|
| `--pf-v5-global--BorderRadius--lg` | `--pf-t--global--border--radius--large` |
| `--pf-v5-global--BorderWidth--md` | `--pf-t--global--border--width--strong` |
| `--pf-v5-global--BoxShadow--lg` | `--pf-t--global--box-shadow--lg` |
| `--pf-v5-global--FontFamily--text` | `--pf-t--global--font--family--body` |
| `--pf-v5-global--FontSize--2xl` | `--pf-t--global--font--size--2xl` |
| `--pf-v5-global--FontWeight--bold` | `--pf-t--global--font--weight--heading--bold` |
| `--pf-v5-global--spacer--lg` | `--pf-t--global--spacer--lg` |
| `--pf-v5-global--gutter` | `--pf-t--global--spacer--gutter--default` |
| `--pf-v5-global--ZIndex--lg` | `--pf-t--global--z-index--lg` |
| `--pf-v5-global--Transition` | `--pf-t--global--transition` |

---

### 1.2 V5 Tokens With No Direct Mapping

#### Tokens Marked as "SKIP" (7 tokens - Removed Without Replacement)

| Token | Original V5 Value | Reason for Removal |
|-------|-------------------|-------------------|
| `global_BoxShadow_inset` | `inset 0 0 0.625rem 0 rgba(3,3,3,0.25)` | Inset shadows not in v6 design system |
| `global_arrow_width` | `0.9375rem` | Arrow components restructured |
| `global_arrow_width_lg` | `1.5625rem` | Arrow components restructured |
| `global_font_path` | Font asset path | Build system changes |
| `global_fonticon_path` | Icon font path | Icon approach changed |
| `global_target_size_MinHeight` | `44px` | Touch target sizing approach changed |
| `global_target_size_MinWidth` | `44px` | Touch target sizing approach changed |

#### Color Tokens (~168 tokens - Require Human Judgment)

All color tokens are replaced with the placeholder `t_temp_dev_tbd` (React) or `--pf-t--temp--dev--tbd` (CSS).

**Categories of color tokens requiring manual selection:**

| Category | Sample V5 Tokens | Count |
|----------|------------------|-------|
| **Palette Colors** | `global_palette_blue_50` through `_700`, `red_*`, `green_*`, `orange_*`, `purple_*`, `cyan_*`, `gold_*` | ~100 |
| **Background Colors** | `global_BackgroundColor_100`, `_200`, `dark_100` through `_400`, `light_100` through `_300` | ~15 |
| **Primary/Secondary** | `global_primary_color_100` through `_200`, `global_secondary_color_100` | ~5 |
| **Semantic Colors** | `global_success_color_*`, `global_warning_color_*`, `global_danger_color_*`, `global_info_color_*` | ~20 |
| **Link Colors** | `global_link_Color`, `global_link_Color_hover`, `_visited`, `_dark`, `_light` | ~10 |
| **Text/Icon Colors** | `global_Color_*`, `global_active_color_*`, `global_disabled_color_*`, `global_icon_Color_*` | ~18 |

#### Component-Specific Tokens (~2,680 tokens - No V6 Equivalents)

These tokens are listed in `oldTokens.ts` and represent internal component styling that has changed significantly.

**Token naming pattern:**
```
c_[component]_[element]_[modifier]_[property]
```

**Examples by component:**

| Component | Sample Tokens | Approximate Count |
|-----------|---------------|-------------------|
| Button | `c_button_PaddingBottom`, `c_button_m_primary_active_BackgroundColor`, `c_button_m_link_m_inline_PaddingBottom` | ~150 |
| Card | `c_card_BoxShadow`, `c_card__actions_MarginBottom`, `c_card_m_compact_child_PaddingBottom` | ~80 |
| Alert | `c_alert_BorderTopColor`, `c_alert__icon_MarginRight`, `c_alert_m_danger_BorderTopColor` | ~60 |
| Form | `c_form__actions_MarginBottom`, `c_form_control_PaddingBottom`, `c_form__helper_text_MarginTop` | ~100 |
| Navigation | `c_nav__item_MarginTop`, `c_nav__link_FontSize`, `c_nav__scroll_button_Width` | ~80 |
| Table | `c_table_cell_PaddingTop`, `c_table__sort_button_MinWidth`, `c_table_m_compact_cell_PaddingTop` | ~120 |
| Modal | `c_modal_box_Width`, `c_modal_box__header_PaddingTop`, `c_modal_box__body_PaddingBottom` | ~50 |
| Dropdown | `c_dropdown__toggle_PaddingTop`, `c_dropdown__menu_MinWidth`, `c_dropdown_m_top_menu_Top` | ~70 |
| Page | `c_page__sidebar_Width`, `c_page__main_section_PaddingTop`, `c_page_header_BackgroundColor` | ~60 |
| Other | Accordion, Badge, Breadcrumb, Chip, DataList, Drawer, EmptyState, Expandable, Label, List, Menu, Panel, Popover, Progress, Select, Sidebar, Spinner, Switch, Tabs, Tile, Title, Toolbar, Tooltip, Wizard, etc. | ~1,910 |

---

### 1.3 New V6 Tokens (No V5 Equivalent)

V6 introduces new semantic tokens without direct V5 predecessors. The `tokensToPrefixWithT` set contains **600+ tokens** that are new or restructured in V6.

**New Token Categories:**

| Category | Examples | Purpose |
|----------|----------|---------|
| **Status Colors** | `t_global_text_color_status_success_default`, `t_global_background_color_status_warning_default` | Context-specific status styling |
| **Action Colors** | `t_global_background_color_action_plain_clicked`, `t_global_border_color_action_default` | Interactive element states |
| **Nonstatus Colors** | `t_global_icon_color_nonstatus_purple_default`, `t_global_text_color_nonstatus_teal_default` | Non-semantic color options |
| **Severity Colors** | `t_global_icon_color_severity_critical_default`, `t_global_border_color_severity_major_default` | Severity indicators |
| **Motion Tokens** | `t_global_motion_duration_fade_short`, `t_global_motion_timing_function_default` | Animation/transition timing |
| **Chart Colors** | `t_chart_color_blue_100` through `_500`, multi-color ordered/unordered scales | Data visualization |
| **Semantic Text** | `t_global_text_color_regular`, `t_global_text_color_subtle`, `t_global_text_color_on_dark_default` | Context-aware text colors |
| **Control Spacing** | `t_global_spacer_control_vertical_default`, `t_global_spacer_control_horizontal_default` | Form control spacing |
| **Gap Tokens** | `t_global_spacer_gap_text_to_element_default`, `t_global_spacer_gap_group_to_group_default` | Layout gap values |

---

## 2. Detection Patterns

### 2.1 CSS Variable Detection

#### Primary Detection Regex

```regex
/(?<!:)(--pf-v5-[\w-]+)/g
```

**Explanation:**
- `(?<!:)` - Negative lookbehind prevents matching codemod comment annotations (e.g., `/* CODEMODS: original v5 color was: --pf-v5-... */`)
- `--pf-v5-` - Matches the v5 CSS variable prefix
- `[\w-]+` - Matches word characters and hyphens (the token name)
- `g` - Global flag for multiple matches per line

#### File Types to Process

| Extension | Content Type |
|-----------|--------------|
| `.css` | Stylesheets |
| `.scss` | Sass stylesheets |
| `.less` | Less stylesheets |
| `.md` | Markdown documentation |
| `.ts`, `.tsx` | TypeScript with inline styles |
| `.js`, `.jsx` | JavaScript with inline styles |

**Default extension regex:**
```regex
/\.(s?css|less|md)$/
```

#### Extended Detection for Component Tokens

```regex
/--pf-v5-c-[\w-]+/g
```

Matches component-specific tokens like `--pf-v5-c-button--m-primary--BackgroundColor`.

#### Detection for React Token Imports

**Pattern for import statements:**
```regex
/from\s+['"]@patternfly\/react-tokens.*['"]/
```

**AST node types to process:**
- `ImportSpecifier` - Named imports: `import { token } from '...'`
- `ImportDefaultSpecifier` - Default imports: `import token from '...'`
- `Identifier` - Token usage in code
- `Literal` - String values containing CSS variable references

#### Detection for CSS Variable Usage in JavaScript

```regex
/var\(([^)]+)\)/g
```

Matches `var(--pf-v5-global--Color--100)` patterns in inline styles.

---

### 2.2 Custom Override Detection

Custom CSS overrides are NOT detected by pf-codemods. Tooling should scan for these patterns:

#### Pattern 1: Direct Variable Override

```regex
/\{\s*--pf-v5-[\w-]+\s*:/
```

Matches declarations like:
```css
.my-component {
  --pf-v5-c-button--m-primary--BackgroundColor: purple;
}
```

#### Pattern 2: Nested PatternFly Selectors

```regex
/\.pf-v5-[cul]-[\w-]+\s*\{/
```

Matches selectors targeting PatternFly internals:
```css
.my-wrapper .pf-v5-c-card .pf-v5-c-card__body {
  padding: 0;
}
```

#### Pattern 3: PatternFly Variable Usage in Media Queries

```regex
/@media[^{]*\{[^}]*--pf-v5-/
```

Matches breakpoint-specific overrides:
```css
@media (max-width: 576px) {
  .mobile-compact {
    --pf-v5-global--spacer--md: 0.5rem;
  }
}
```

---

### 2.3 Directional Property Detection

V6 uses logical properties (LTR/RTL-aware) instead of physical directions.

**Detection regex:**
```regex
/(Left|Right|Top|Bottom)$/
```

**Transformation map:**

| Physical Direction | Logical Property (LTR) | Logical Property (RTL) |
|--------------------|------------------------|------------------------|
| `Left` | `InlineStart` | `InlineEnd` |
| `Right` | `InlineEnd` | `InlineStart` |
| `Top` | `BlockStart` | `BlockStart` |
| `Bottom` | `BlockEnd` | `BlockEnd` |

---

## 3. Replacement Heuristics

### 3.1 Semantic Similarity Heuristics

When suggesting V6 token replacements for unmapped V5 tokens, use these heuristics:

#### Heuristic 1: Property Context

Map based on the CSS property being styled:

| CSS Property | V6 Token Category | Example |
|--------------|-------------------|---------|
| `color` | `text--color` | `--pf-t--global--text--color--regular` |
| `background-color` | `background--color` | `--pf-t--global--background--color--primary--default` |
| `border-color` | `border--color` | `--pf-t--global--border--color--default` |
| `fill` (SVG) | `icon--color` | `--pf-t--global--icon--color--brand--default` |
| `stroke` (SVG) | `icon--color` | `--pf-t--global--icon--color--brand--default` |

#### Heuristic 2: Semantic Intent Keywords

Extract semantic meaning from V5 token names:

| V5 Keyword | V6 Semantic Token Pattern |
|------------|---------------------------|
| `primary` | `--brand--default` |
| `secondary` | `--secondary--default` |
| `success` | `--status--success--default` |
| `warning` | `--status--warning--default` |
| `danger`, `error` | `--status--danger--default` |
| `info` | `--status--info--default` |
| `link` | `--link--default` |
| `disabled` | `--disabled` |
| `hover` | `--hover` |
| `active`, `clicked` | `--clicked` |
| `dark` | `--on-dark--default` |
| `light` | `--on-light--default` |

#### Heuristic 3: Numeric Suffix Translation

V5 used numeric suffixes (100, 200, 300...) that roughly map to semantic concepts:

| V5 Numeric | Likely V6 Semantic |
|------------|-------------------|
| `100` | `primary--default` or `regular` |
| `200` | `secondary--default` or `subtle` |
| `300` | `tertiary--default` |
| `400-500` | Status/brand specific |
| `dark_100-400` | `on-dark` variants |
| `light_100-300` | `on-light` variants |

---

### 3.2 Context-Based Suggestion Matrix

For tokens that split into multiple V6 options:

#### V5 `global_primary_color_100` → V6 Options

| Usage Context | Suggested V6 Token | Confidence |
|---------------|-------------------|------------|
| Text color | `t_global_text_color_brand_default` | High |
| Background | `t_global_background_color_brand_default` | High |
| Border | `t_global_border_color_brand_default` | High |
| Icon fill | `t_global_icon_color_brand_default` | High |
| Generic | `t_global_color_brand_default` | Medium |

#### V5 `global_link_Color` → V6 Options

| Usage Context | Suggested V6 Token | Confidence |
|---------------|-------------------|------------|
| Anchor text | `t_global_text_color_link_default` | High |
| Icon in link | `t_global_icon_color_brand_default` | Medium |
| Hover state | `t_global_text_color_link_hover` | High |

#### V5 `global_success_color_100` → V6 Options

| Usage Context | Suggested V6 Token | Confidence |
|---------------|-------------------|------------|
| Alert text | `t_global_text_color_status_success_default` | High |
| Alert background | `t_global_background_color_status_success_default` | High |
| Alert border | `t_global_border_color_status_success_default` | High |
| Success icon | `t_global_icon_color_status_success_default` | High |

---

### 3.3 Confidence Scoring Model

Assign confidence scores to replacement suggestions:

| Confidence Level | Score | Criteria |
|------------------|-------|----------|
| **High** (80-100%) | Automated replacement safe | Direct mapping exists in `globalNonColorTokensMap`; or single unambiguous V6 token matches context |
| **Medium** (50-79%) | Suggestion with review | Multiple V6 options exist; context analysis narrows to likely candidate |
| **Low** (20-49%) | Manual selection required | No clear mapping; semantic meaning unclear; multiple equally valid options |
| **None** (0-19%) | Removed functionality | Token marked "SKIP"; no V6 equivalent concept exists |

**Confidence Factors:**

| Factor | Weight | Description |
|--------|--------|-------------|
| Direct mapping exists | +40% | Entry in `globalNonColorTokensMap` |
| Single context match | +30% | Only one V6 token matches CSS property |
| Semantic keyword match | +20% | V5 token name contains clear semantic intent |
| Numeric to semantic | +10% | Clear pattern for numeric → semantic conversion |
| Multiple valid options | -20% | More than one reasonable V6 replacement |
| Component-specific | -30% | Token from `oldTokens` set (no mapping) |
| Marked SKIP | -100% | Explicitly removed functionality |

---

## 4. Implementation Architecture

### 4.1 Detection Module

```
┌─────────────────────────────────────────────────────────────┐
│                     Detection Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ File        │    │ Pattern     │    │ Token       │     │
│  │ Discovery   │───▶│ Matching    │───▶│ Extraction  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                 │                   │             │
│         ▼                 ▼                   ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Extension   │    │ Regex       │    │ Token       │     │
│  │ Filter      │    │ Engine      │    │ Catalog     │     │
│  │             │    │             │    │             │     │
│  │ .css        │    │ CSS vars    │    │ Category    │     │
│  │ .scss       │    │ Imports     │    │ Location    │     │
│  │ .tsx        │    │ Overrides   │    │ Context     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Input:** Directory path, file extension filter, exclusion patterns
**Output:** List of `{file, line, column, token, context, category}` records

### 4.2 Suggestion Module

```
┌─────────────────────────────────────────────────────────────┐
│                    Suggestion Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Token       │    │ Mapping     │    │ Confidence  │     │
│  │ Analysis    │───▶│ Lookup      │───▶│ Scoring     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                 │                   │             │
│         ▼                 ▼                   ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Parse       │    │ Check:      │    │ Calculate   │     │
│  │ token name  │    │ - Direct    │    │ confidence  │     │
│  │             │    │ - Color     │    │ based on:   │     │
│  │ Extract:    │    │ - Component │    │ - Mapping   │     │
│  │ - Scope     │    │ - SKIP      │    │ - Context   │     │
│  │ - Property  │    │             │    │ - Semantic  │     │
│  │ - Modifiers │    │ Return:     │    │             │     │
│  │             │    │ - V6 token  │    │ Rank        │     │
│  │             │    │ - Category  │    │ suggestions │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Input:** Detected token, CSS property context, surrounding code
**Output:** List of `{v6Token, confidence, rationale}` suggestions

### 4.3 Data Structures

#### Token Detection Record

```typescript
interface TokenDetection {
  file: string;           // Absolute file path
  line: number;           // 1-indexed line number
  column: number;         // 1-indexed column number
  token: string;          // Full token name (e.g., "--pf-v5-global--Color--100")
  tokenType: 'css-var' | 'react-import' | 'react-usage' | 'override';
  context: {
    property?: string;    // CSS property being set (e.g., "color", "background-color")
    selector?: string;    // CSS selector context
    isOverride: boolean;  // true if overriding a PF variable
    isMediaQuery: boolean;
    importPath?: string;  // For React tokens
  };
  category: 'global-non-color' | 'global-color' | 'component' | 'removed';
}
```

#### Replacement Suggestion

```typescript
interface ReplacementSuggestion {
  originalToken: string;
  suggestedTokens: Array<{
    token: string;        // V6 token name
    confidence: number;   // 0-100
    rationale: string;    // Human-readable explanation
    requiresReview: boolean;
  }>;
  category: 'auto-fixable' | 'needs-review' | 'manual-only' | 'removed';
  documentation?: string; // Link to relevant docs
}
```

---

## 5. Reference Data Sources

### 5.1 pf-codemods Token Lists

| File | Content | Size |
|------|---------|------|
| `oldGlobalTokens.ts` | Non-color + color token maps | ~10KB |
| `oldGlobalCssVarNames.ts` | CSS variable name mappings | ~13KB |
| `oldTokens.ts` | ~2,680 deprecated component tokens | ~166KB |
| `oldCssVarNames.ts` | Legacy CSS variable names | ~201KB |
| `tokensToPrefixWithT.ts` | 600+ tokens needing t_ prefix | ~34KB |
| `v6DirectionCssVars.ts` | Directional CSS variables | ~70KB |
| `v6DirectionTokens.ts` | Directional token mappings | ~58KB |

**Repository:** https://github.com/patternfly/pf-codemods
**Path:** `packages/shared-codemod-helpers/src/tokenLists/`

### 5.2 PatternFly Documentation

| Resource | URL | Content |
|----------|-----|---------|
| All Tokens | https://www.patternfly.org/tokens/all-patternfly-tokens | Complete V6 token reference |
| About Tokens | https://www.patternfly.org/tokens/about-tokens | Token system overview |
| Upgrade Guide | https://www.patternfly.org/get-started/upgrade | Migration instructions |

### 5.3 Token Value Changes

Some tokens that have "mappings" actually have different values between V5 and V6:

| Token | V5 Value | V6 Value | Impact |
|-------|----------|----------|--------|
| `global_FontSize_2xl` | `1.5rem` | `1.375rem` | Text slightly smaller |
| `global_icon_FontSize_lg` | `3.375rem` | `2.25rem` | Icons significantly smaller |
| `global_icon_FontSize_xl` | `3.375rem` | `2.25rem` | Icons significantly smaller |

Tooling should flag these for visual verification even when mapping exists.

---

## 6. Checkpoint Verification

This document provides implementation-ready technical detail to:

1. **Create mapping documentation**:
   - 64 global non-color token mappings (Table 1.1)
   - 168 color tokens requiring human judgment (Section 1.2)
   - 2,680 component tokens with no V6 equivalent (Section 1.2)
   - 600+ new V6 tokens (Section 1.3)

2. **Implement detection patterns**:
   - Primary regex: `/(?<!:)(--pf-v5-[\w-]+)/g` (Section 2.1)
   - File type filtering: `\.(s?css|less|md)$` (Section 2.1)
   - AST node types for React (Section 2.1)
   - Custom override patterns (Section 2.2)

3. **Build suggestion heuristics**:
   - Property context mapping (Section 3.1)
   - Semantic intent keyword matching (Section 3.1)
   - Context-based suggestion matrix (Section 3.2)
   - Confidence scoring model (Section 3.3)

4. **Prototype architecture**:
   - Detection pipeline design (Section 4.1)
   - Suggestion pipeline design (Section 4.2)
   - TypeScript data structures (Section 4.3)

---

## References

- [PatternFly Tokens Documentation](https://www.patternfly.org/tokens/about-tokens/)
- [PatternFly All Tokens](https://www.patternfly.org/tokens/all-patternfly-tokens)
- [PatternFly Upgrade Guide](https://www.patternfly.org/get-started/upgrade)
- [pf-codemods Repository](https://github.com/patternfly/pf-codemods)
- Phase 1: Design Token Fundamentals (01_design_tokens_fundamentals.md)
- Phase 2: pf-codemods Analysis (02_pf_codemods_analysis.md)
- Phase 3: Migration Gaps Analysis (03_migration_gaps_analysis.md)
