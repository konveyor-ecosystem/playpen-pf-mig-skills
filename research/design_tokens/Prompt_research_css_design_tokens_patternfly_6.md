# Research Prompt: CSS Design Token Migration - PatternFly 5 to 6

## Purpose

This prompt guides research into CSS Design Token migration challenges when upgrading from PatternFly 5 to PatternFly 6. The research will inform the development of complementary tooling to address gaps not covered by existing tools like `pf-codemods`.

## Target Audience

- **Primary**: Tool builders creating migration assistance products
- **Secondary**: Developers and coding agents needing rapid onboarding to this problem space

## Scope & Boundaries

| Boundary | Constraint |
|----------|------------|
| Focus Area | CSS issues with Design Tokens (not JS API changes) |
| Version | PatternFly v5 → v6 only |
| Framework | React implementations only |
| Problem Space | Custom CSS overrides without 1:1 token mappings |

## Key Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| PatternFly Upgrade Guide | https://www.patternfly.org/get-started/upgrade | Migration starting point |
| pf-codemods v6 Rules | https://github.com/patternfly/pf-codemods/tree/main/packages/eslint-plugin-pf-codemods/src/rules/v6 | Understand existing tooling coverage |
| PatternFly Tokens Docs | https://www.patternfly.org/tokens/about-tokens/ | Token architecture reference |

---

## Research Phases

### Phase 1: Foundational Understanding

**Objective**: Establish conceptual knowledge of CSS Design Tokens and PatternFly's implementation.

**Tasks**:
1. Research CSS Design Tokens as a general concept
   - What they are and why they exist
   - How they differ from CSS variables
   - The W3C Design Tokens specification
   - Common implementation patterns

2. Document PatternFly 6's token architecture
   - Three-layer system: Palette → Base → Semantic tokens
   - Naming conventions (`--pf-t--[scope]--[component]--[property]--[concept]--[variant]--[state]`)
   - Token types (color, spacing, typography, etc.)

3. Understand the v5 → v6 naming transformation
   - Example: `--pf-v5-global--FontSize--lg` → `--pf-t--global--font--size--lg`
   - React token format changes (`global_FontSize_lg` → `t_global_font_size_lg`)

**Output**: `research/01_design_tokens_fundamentals.md`

**Checkpoint**: Can explain design tokens, PatternFly's token layers, and the naming changes to a developer unfamiliar with the topic.

---

### Phase 2: Existing Tooling Analysis

**Objective**: Understand what `pf-codemods` handles and identify its boundaries.

**Tasks**:
1. Analyze the pf-codemods v6 rules repository
   - Catalog all CSS/token-related codemods
   - Document what transformations each rule performs
   - Identify the detection patterns used (regex, AST, etc.)

2. Focus on these specific codemods:
   - `class-name-updater` - what it catches and misses
   - `tokens-update` - React token transformations
   - `css-vars-updater` - CSS variable updates in non-React files

3. Document the tool's stated limitations
   - "Hot pink" fallback for unmatchable tokens
   - Scenarios explicitly marked as requiring manual intervention

**Output**: `research/02_pf_codemods_analysis.md`

**Checkpoint**: Can articulate exactly what pf-codemods handles and where it explicitly stops.

---

### Phase 3: Gap Identification

**Objective**: Identify and categorize CSS override scenarios that require manual intervention.

**Tasks**:
1. Research scenarios where 1:1 token mappings don't exist
   - Removed v5 variables with no v6 equivalent
   - Consolidated variables (multiple v5 → single v6)
   - Split variables (single v5 → multiple v6)
   - Semantic meaning changes

2. Categorize custom CSS override patterns
   - Direct variable overrides (`--pf-v5-*` in custom CSS)
   - Class-based overrides (`.pf-v5-c-*` selectors)
   - Nested/compound selectors
   - Media query interactions with breakpoint changes (px → rem)

3. Document the "decision points" where human judgment is required
   - Choosing between multiple possible v6 tokens
   - Deciding if an override is still needed
   - Handling removed functionality

**Output**: `research/03_migration_gaps_analysis.md`

**Checkpoint**: Have a categorized inventory of gap types with concrete examples of each.

---

### Phase 4: Technical Deep Dive

**Objective**: Gather implementation-ready details for tooling development.

**Tasks**:
1. Create detailed mapping documentation
   - V5 variables → V6 tokens (where mappings exist)
   - V5 variables with no direct mapping (requires decision)
   - New V6 tokens without V5 predecessors

2. Document detection patterns
   - Regex patterns for identifying v5 CSS variables in code
   - File types and locations where overrides commonly appear
   - AST considerations for more sophisticated parsing

3. Identify heuristics for suggesting replacements
   - Semantic similarity matching
   - Context-based suggestions (component, usage pattern)
   - Confidence scoring for automated vs. manual resolution

**Output**: `research/04_technical_implementation_details.md`

**Checkpoint**: Have enough technical detail to begin prototyping detection and suggestion logic.

---

### Phase 5: Customer Journey Mapping

**Objective**: Document the technical workflow developers follow during migration.

**Tasks**:
1. Map the migration workflow
   - Discovery: How do developers find their CSS overrides?
   - Analysis: How do they determine what needs to change?
   - Resolution: How do they find the right replacement token?
   - Validation: How do they verify the migration worked?

2. Identify common scenarios by frequency/difficulty
   - Quick wins (straightforward mappings)
   - Moderate effort (requires some investigation)
   - Complex cases (requires significant decision-making)

3. Document pain points at each workflow stage
   - What information is missing?
   - What decisions are hardest?
   - Where do developers get stuck?

**Output**: `research/05_migration_workflow_analysis.md`

**Checkpoint**: Can describe the end-to-end technical journey with identified intervention points for tooling.

---

### Phase 6: Synthesis & Recommendations

**Objective**: Consolidate findings into actionable insights for tool development.

**Tasks**:
1. Prioritize gap categories by:
   - Frequency (how often developers encounter this)
   - Difficulty (how hard it is to resolve manually)
   - Automation potential (feasibility of tooling assistance)

2. Define tool requirements
   - Must-have capabilities
   - Nice-to-have features
   - Out-of-scope items

3. Create a summary document for rapid onboarding
   - Executive summary (1 page)
   - Key findings
   - Recommended next steps

**Output**:
- `research/06_synthesis_and_recommendations.md`
- `research/00_executive_summary.md`

**Checkpoint**: A new team member can read the executive summary and understand the problem space, then dive into specific research files for detail.

---

## Success Criteria

After completing this research, readers should be able to:

- [ ] Understand the CSS Design Token problem space well enough to define tool requirements
- [ ] Identify specific categories of CSS overrides that need manual intervention
- [ ] Reference a prioritized list of migration scenarios by frequency/difficulty
- [ ] Possess enough technical detail to start prototyping a complementary tool

## Output File Naming Convention

All research outputs should follow this pattern:
```
research/
├── 00_executive_summary.md
├── 01_design_tokens_fundamentals.md
├── 02_pf_codemods_analysis.md
├── 03_migration_gaps_analysis.md
├── 04_technical_implementation_details.md
├── 05_migration_workflow_analysis.md
└── 06_synthesis_and_recommendations.md
```

## Execution Notes

- Complete phases sequentially; each builds on the previous
- Create the output markdown file at the end of each phase before proceeding
- If a phase reveals information that changes earlier findings, update previous documents
- Use code examples liberally - concrete beats abstract
- When documenting gaps, always include:
  - The v5 code pattern
  - Why pf-codemods doesn't handle it
  - What the developer must decide
  - Potential v6 resolution options
