# PRD: CSS Design Token Migration Research (PatternFly 5 to 6)

## Introduction

This PRD defines a structured research initiative to investigate CSS Design Token migration challenges when upgrading from PatternFly 5 to PatternFly 6. The research will be executed by an AI agent with human review, producing documentation that informs the development of complementary tooling to address gaps not covered by existing tools like `pf-codemods`.

The core problem: PatternFly 6 introduces a new design token architecture with different naming conventions. While `pf-codemods` handles many automated transformations, custom CSS overrides often lack 1:1 token mappings and require human judgment. This research identifies and categorizes those gaps.

## Goals

- Enable an AI agent to autonomously execute all 6 research phases with clear self-verification checkpoints
- Document CSS Design Token fundamentals and PatternFly's implementation
- Analyze existing `pf-codemods` tooling to understand its coverage boundaries
- Identify and categorize migration scenarios requiring manual intervention
- Produce technical details sufficient to begin prototyping complementary tooling
- Create a rapid-onboarding executive summary for new team members

## User Stories

### US-001: Phase 1 - Foundational Understanding
**Description:** As a tool builder, I need foundational knowledge of CSS Design Tokens and PatternFly's implementation so that I understand the problem domain before analyzing gaps.

**Acceptance Criteria:**
- [ ] Research CSS Design Tokens as a general concept (what they are, W3C spec, implementation patterns)
- [ ] Document PatternFly 6's three-layer token system: Palette → Base → Semantic
- [ ] Document naming conventions (`--pf-t--[scope]--[component]--[property]--[concept]--[variant]--[state]`)
- [ ] Document v5 → v6 naming transformations with examples
- [ ] Document React token format changes (`global_FontSize_lg` → `t_global_font_size_lg`)
- [ ] Output saved to `research/01_design_tokens_fundamentals.md`
- [ ] Checkpoint: Can explain design tokens, PatternFly's token layers, and naming changes to an unfamiliar developer

**Key Resources:**
- https://www.patternfly.org/get-started/upgrade
- https://www.patternfly.org/tokens/about-tokens/

---

### US-002: Phase 2 - Existing Tooling Analysis
**Description:** As a tool builder, I need to understand what `pf-codemods` handles so that I can identify where complementary tooling is needed.

**Acceptance Criteria:**
- [ ] Analyze pf-codemods v6 rules repository structure
- [ ] Catalog all CSS/token-related codemods with their transformation logic
- [ ] Document detection patterns used (regex, AST, etc.)
- [ ] Deep-dive on `class-name-updater` - what it catches and misses
- [ ] Deep-dive on `tokens-update` - React token transformations
- [ ] Deep-dive on `css-vars-updater` - CSS variable updates in non-React files
- [ ] Document "hot pink" fallback behavior for unmatchable tokens
- [ ] List scenarios explicitly marked as requiring manual intervention
- [ ] Output saved to `research/02_pf_codemods_analysis.md`
- [ ] Checkpoint: Can articulate exactly what pf-codemods handles and where it explicitly stops

**Key Resources:**
- https://github.com/patternfly/pf-codemods/tree/main/packages/eslint-plugin-pf-codemods/src/rules/v6

---

### US-003: Phase 3 - Gap Identification
**Description:** As a tool builder, I need a categorized inventory of migration gaps so that I can prioritize tooling development efforts.

**Acceptance Criteria:**
- [ ] Research scenarios where 1:1 token mappings don't exist:
  - Removed v5 variables with no v6 equivalent
  - Consolidated variables (multiple v5 → single v6)
  - Split variables (single v5 → multiple v6)
  - Semantic meaning changes
- [ ] Categorize custom CSS override patterns:
  - Direct variable overrides (`--pf-v5-*` in custom CSS)
  - Class-based overrides (`.pf-v5-c-*` selectors)
  - Nested/compound selectors
  - Media query interactions with breakpoint changes (px → rem)
- [ ] Document "decision points" requiring human judgment:
  - Choosing between multiple possible v6 tokens
  - Deciding if an override is still needed
  - Handling removed functionality
- [ ] Each gap category includes concrete code examples
- [ ] Output saved to `research/03_migration_gaps_analysis.md`
- [ ] Checkpoint: Have a categorized inventory of gap types with concrete examples of each

---

### US-004: Phase 4 - Technical Deep Dive
**Description:** As a tool builder, I need implementation-ready technical details so that I can begin prototyping detection and suggestion logic.

**Acceptance Criteria:**
- [ ] Create mapping documentation:
  - V5 variables → V6 tokens (where mappings exist)
  - V5 variables with no direct mapping (requires decision)
  - New V6 tokens without V5 predecessors
- [ ] Document detection patterns:
  - Regex patterns for identifying v5 CSS variables in code
  - File types and locations where overrides commonly appear
  - AST considerations for sophisticated parsing
- [ ] Identify heuristics for suggesting replacements:
  - Semantic similarity matching approaches
  - Context-based suggestions (component, usage pattern)
  - Confidence scoring for automated vs. manual resolution
- [ ] Output saved to `research/04_technical_implementation_details.md`
- [ ] Checkpoint: Have enough technical detail to begin prototyping detection and suggestion logic

---

### US-005: Phase 5 - Migration Workflow Analysis
**Description:** As a tool builder, I need to understand the developer migration workflow so that tooling can intervene at the right points.

**Acceptance Criteria:**
- [ ] Map the complete migration workflow:
  - Discovery: How developers find their CSS overrides
  - Analysis: How they determine what needs to change
  - Resolution: How they find the right replacement token
  - Validation: How they verify the migration worked
- [ ] Categorize scenarios by frequency and difficulty:
  - Quick wins (straightforward mappings)
  - Moderate effort (requires investigation)
  - Complex cases (requires significant decision-making)
- [ ] Document pain points at each workflow stage:
  - What information is missing
  - What decisions are hardest
  - Where developers get stuck
- [ ] Output saved to `research/05_migration_workflow_analysis.md`
- [ ] Checkpoint: Can describe end-to-end technical journey with identified intervention points

---

### US-006: Phase 6 - Synthesis and Recommendations
**Description:** As a tool builder, I need consolidated findings and prioritized recommendations so that I can make informed decisions about tooling development.

**Acceptance Criteria:**
- [ ] Prioritize gap categories by:
  - Frequency (how often developers encounter this)
  - Difficulty (how hard it is to resolve manually)
  - Automation potential (feasibility of tooling assistance)
- [ ] Define tool requirements:
  - Must-have capabilities
  - Nice-to-have features
  - Out-of-scope items
- [ ] Create executive summary for rapid onboarding (1 page)
- [ ] Output saved to `research/06_synthesis_and_recommendations.md`
- [ ] Output saved to `research/00_executive_summary.md`
- [ ] Checkpoint: New team member can read executive summary and understand problem space

---

## Functional Requirements

- FR-1: Execute phases sequentially; each phase builds on previous findings
- FR-2: Create output markdown file at the end of each phase before proceeding
- FR-3: If a phase reveals information that changes earlier findings, update previous documents
- FR-4: Use code examples liberally - concrete beats abstract
- FR-5: When documenting gaps, always include:
  - The v5 code pattern
  - Why pf-codemods doesn't handle it
  - What the developer must decide
  - Potential v6 resolution options
- FR-6: All research outputs follow the defined file naming convention
- FR-7: Each phase must pass its checkpoint criteria before proceeding to the next phase

## Non-Goals

- Building the actual migration tooling (this PRD is research only)
- Covering JavaScript/React API changes (focus is CSS tokens only)
- Supporting versions other than PatternFly 5 → 6
- Supporting non-React frameworks
- Modifying or contributing to `pf-codemods` itself
- Creating automated tests or validation tooling

## Technical Considerations

**Scope Constraints:**
| Boundary | Constraint |
|----------|------------|
| Focus Area | CSS issues with Design Tokens (not JS API changes) |
| Version | PatternFly v5 → v6 only |
| Framework | React implementations only |
| Problem Space | Custom CSS overrides without 1:1 token mappings |

**Key Resources:**
| Resource | URL | Purpose |
|----------|-----|---------|
| PatternFly Upgrade Guide | https://www.patternfly.org/get-started/upgrade | Migration starting point |
| pf-codemods v6 Rules | https://github.com/patternfly/pf-codemods/tree/main/packages/eslint-plugin-pf-codemods/src/rules/v6 | Existing tooling coverage |
| PatternFly Tokens Docs | https://www.patternfly.org/tokens/about-tokens/ | Token architecture reference |

**Output Structure:**
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

## Success Metrics

After completing this research, readers should be able to:
- Understand the CSS Design Token problem space well enough to define tool requirements
- Identify specific categories of CSS overrides that need manual intervention
- Reference a prioritized list of migration scenarios by frequency/difficulty
- Possess enough technical detail to start prototyping a complementary tool
- Onboard a new team member in under 30 minutes using the executive summary

## Open Questions

- Should the research include analysis of real-world PatternFly codebases to validate gap categories?
- Are there PatternFly community resources (Discord, GitHub issues) that should be mined for common migration pain points?
- Should the research produce machine-readable mapping files (JSON/YAML) in addition to markdown documentation?
- What level of detail is needed for the token mapping tables to be useful for tooling?
