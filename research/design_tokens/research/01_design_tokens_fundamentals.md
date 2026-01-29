# Design Tokens Fundamentals

This document provides foundational knowledge of CSS Design Tokens and PatternFly's implementation for developers working on PF5 to PF6 migration tooling.

## What Are Design Tokens?

Design tokens are the **atomic building blocks of a design system**. They are named variables that store visual design attributes such as colors, typography, spacing, shadows, and other style values.

According to the W3C Design Tokens Community Group (DTCG), design tokens represent the "visual language" that teams can share reliably across design tools, codebases, and platforms. The term "design tokens" was coined by the Salesforce design system team (Jon & Jina).

### Key Characteristics

- **Named values**: Each token has a descriptive name that conveys its purpose (e.g., `--pf-t--global--spacer--md`)
- **Platform-agnostic**: Tokens can be transformed into CSS variables, JavaScript constants, iOS/Android values, etc.
- **Single source of truth**: Changes to a token value propagate everywhere it's used
- **Semantic meaning**: Names describe intent/purpose, not just raw values

### W3C Design Tokens Specification

The Design Tokens Community Group published its first stable specification version (2025.10) in October 2025. Key aspects:

- **Vendor-neutral format**: JSON-based specification enabling cross-tool interoperability
- **Theming support**: Built-in mechanisms for theme variations
- **Modern color spaces**: Support for contemporary color formats
- **Wide adoption**: Supported by tools like Adobe, Figma, Sketch, and Style Dictionary

The specification enables design decisions to scale across teams and products without proprietary format lock-in.

### Benefits of Design Tokens

1. **Consistency**: Uniform styling across products by ensuring identical styles apply to the same use cases
2. **Maintainability**: Design system updates automatically reflect across all implementations
3. **Collaboration**: Common vocabulary between designers and developers
4. **Scalability**: Enables theming, white-labeling, and multi-brand systems

---

## PatternFly 6's Three-Layer Token System

PatternFly 6 implements a hierarchical token architecture with three distinct layers. This structure provides flexibility while maintaining consistency.

### Layer 1: Palette Tokens

**Purpose**: Foundation layer containing raw color values from PatternFly's color palettes.

**Characteristics**:
- Lowest abstraction level
- Direct color values (hex, rgb, etc.)
- Named by color family and shade

**Example use case**: Defining the base red, blue, green colors that will be referenced by higher layers.

### Layer 2: Base Tokens

**Purpose**: Expands palette application to specific design concepts like spacing, borders, and sizing.

**Characteristics**:
- Organized numerically (sm, md, lg, xl, etc.)
- No duplicate values within groups
- Covers spacing, borders, typography scales

**Examples**:
- `pf-t--global--spacer--md` = "1rem"
- `pf-t--global--border--width--regular`

### Layer 3: Semantic Tokens

**Purpose**: Top-level tokens with conceptual grouping and intentional naming. **These are recommended for most use cases.**

**Characteristics**:
- Highest abstraction level
- Named by purpose/intent rather than appearance
- Include state variants (default, hover, clicked, disabled)

**Examples**:
- `pf-t--global--background--color--action--plain--clicked`
- `pf-t--global--text--color--status--success--default`

### Token Categories in PatternFly 6

PatternFly 6 organizes semantic tokens into these primary categories:

| Category | Description | Example Tokens |
|----------|-------------|----------------|
| **Icon colors** | Brand, status, severity, nonstatus variants | icon--color--brand--default |
| **Border** | Colors, widths, control/status/action variants | border--color--status--warning |
| **Background** | Primary, secondary, tertiary, floating, action, disabled | background--color--primary--default |
| **Text** | Link, brand, status, nonstatus, semantic states | text--color--link--hover |
| **Spacing** | xs through 4xl, control and action variants | spacer--lg, spacer--action--horizontal |
| **Typography** | Font families, sizes, weights, line-height | font--size--heading--h1 |
| **Sizing** | Icon sizes, border radius, z-index | border--radius--pill |
| **Box shadows** | sm, md, lg sizes | box-shadow--lg |

---

## Token Naming Conventions

### PatternFly 6 Token Format

PatternFly 6 uses a structured naming convention:

```
--pf-t--[scope]--[component]--[property]--[concept]--[variant]--[state]
```

### Naming Segments Explained

| Segment | Description | Examples |
|---------|-------------|----------|
| **Prefix** | Always `--pf-t--` in PF6 | `--pf-t--` |
| **Scope** | Token range | `global`, `chart` |
| **Component** | Related component type | `icon`, `background`, `text`, `border` |
| **Property** | Style attribute | `color`, `size`, `radius`, `width` |
| **Concept** | Higher-level category | `status`, `primary`, `action`, `brand` |
| **Variant** | Specific option | `link`, `warning`, `success`, `danger` |
| **State** | Component condition | `default`, `hover`, `active`, `clicked`, `disabled` |

### Complete Token Name Examples

```css
/* Background action color in clicked state */
--pf-t--global--background--color--action--plain--clicked

/* Backdrop background with default styling */
--pf-t--global--background--color--backdrop--default

/* Standard border width */
--pf-t--global--border--width--regular

/* Heading typography */
--pf-t--global--font--size--heading--h1

/* Medium spacing */
--pf-t--global--spacer--md

/* Maximum border radius (pill shape) */
--pf-t--global--border--radius--pill
```

---

## V5 to V6 Naming Transformations

PatternFly 6 introduces significant changes to variable naming. Understanding these transformations is critical for migration tooling.

### CSS Variable Transformation Pattern

| Aspect | PatternFly 5 | PatternFly 6 |
|--------|--------------|--------------|
| **Prefix** | `--pf-v5-` | `--pf-t--` |
| **Naming style** | camelCase | kebab-case |
| **Separators** | Single dash | Double dash |

### Concrete Examples

```css
/* Font size - large */
--pf-v5-global--FontSize--lg    →    --pf-t--global--font--size--lg

/* Global spacing */
--pf-v5-global--spacer--md      →    --pf-t--global--spacer--md

/* Primary color */
--pf-v5-global--primary-color--100    →    (requires semantic mapping)
```

### Key Transformation Rules

1. **Prefix change**: `--pf-v5-` becomes `--pf-t--`
2. **Case conversion**: `FontSize` becomes `font--size` (camelCase to kebab-case with double-dash)
3. **Separator standardization**: All segments separated by double dashes `--`
4. **Semantic restructuring**: Many v5 tokens don't have 1:1 mappings and require choosing appropriate semantic tokens

### Tokens Without 1:1 Mappings

A significant challenge in migration: **many v5 tokens have no direct v6 equivalent**. This occurs due to:

- **Removal**: Some tokens were deprecated
- **Consolidation**: Multiple v5 tokens merged into one v6 token
- **Splitting**: One v5 token became multiple v6 tokens
- **Semantic changes**: Token purpose/meaning changed

---

## React Token Format Changes

PatternFly provides tokens as JavaScript/TypeScript constants for use in React applications. The format changed significantly from v5 to v6.

### Transformation Pattern

| Aspect | PatternFly 5 | PatternFly 6 |
|--------|--------------|--------------|
| **Prefix** | None (starts with scope) | `t_` prefix |
| **Naming style** | mixed_Case | all_lowercase |
| **Word separator** | Underscores, mixed case | Underscores only |

### Concrete Examples

```typescript
// Font size large
global_FontSize_lg        →    t_global_font_size_lg

// Spacing medium
global_spacer_md          →    t_global_spacer_md

// Background color
global_BackgroundColor_100    →    t_global_background_color_primary_default
```

### Key Transformation Rules

1. **Add `t_` prefix**: All v6 React tokens start with `t_`
2. **Lowercase everything**: `FontSize` becomes `font_size`
3. **Semantic remapping**: Like CSS variables, many React tokens require semantic analysis to find the appropriate v6 token

### Critical Note for Tooling

The PatternFly documentation explicitly states:

> "tokens in your code point to old global variables" and requires manual replacement when "there is often no 1:1 match for a PatternFly 5 and PatternFly 6 React token."

This means automated tooling must handle:
- Direct transformations (where 1:1 mapping exists)
- Flagging cases requiring manual intervention
- Providing suggestions based on semantic analysis

---

## Summary: Key Takeaways for Migration Tooling

1. **Design tokens are semantic variables** that enable consistent, maintainable styling

2. **PatternFly 6 uses a three-layer system**:
   - Palette (raw values) → Base (concepts) → Semantic (intent)
   - Semantic tokens are recommended for application code

3. **Naming conventions changed fundamentally**:
   - CSS: `--pf-v5-global--FontSize--lg` → `--pf-t--global--font--size--lg`
   - React: `global_FontSize_lg` → `t_global_font_size_lg`

4. **Many migrations require human judgment**:
   - No 1:1 mappings for many tokens
   - Semantic context needed to choose correct replacement
   - pf-codemods handles some cases but flags others for manual review

5. **The W3C specification (2025.10)** provides industry-standard token formats that PatternFly aligns with

---

## References

- [PatternFly Tokens Documentation](https://www.patternfly.org/tokens/about-tokens/)
- [PatternFly Upgrade Guide](https://www.patternfly.org/get-started/upgrade)
- [All PatternFly Tokens](https://www.patternfly.org/tokens/all-patternfly-tokens)
- [W3C Design Tokens Community Group](https://www.w3.org/community/design-tokens/)
- [Design Tokens Specification](https://www.designtokens.org/)
