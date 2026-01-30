---
name: pf6-migrate
description: Migrate a PatternFly 5 application to PatternFly 6 with visual verification. Use when upgrading a PatternFly 5 codebase to PatternFly 6, migrating PF5 to PF6, or when asked to upgrade PatternFly.
disable-model-invocation: true
---

# PatternFly 5 to 6 Migration with Visual Verification

Migrate a PatternFly 5 application to PatternFly 6 using the official upgrade guide and visual comparison to ensure the migrated UI matches the original.

## Prerequisites Check

**CRITICAL: Before proceeding, verify the Chrome MCP server is available.**

Run a test to check if the Chrome MCP server is installed and accessible:

1. Check if you have access to Chrome MCP tools.
2. If Chrome MCP tools are NOT available, stop immediately and inform the user:

```
ERROR: Chrome MCP server is not installed or not configured.

This skill requires the Chrome MCP server to perform visual comparison
between the original and migrated versions of the application.

To install the Chrome MCP server, add it to your Claude Code MCP configuration.
See: https://github.com/anthropics/claude-code/blob/main/docs/mcp.md

After installing, restart Claude Code and try again.
```

Do NOT proceed with migration if Chrome MCP is unavailable.

---

## Step 1: Create a Migration Branch

Create a new git branch for the migration work:

```bash
git checkout -b pf6-migration
```

If the branch already exists, ask the user how to proceed (checkout existing, create new name, or abort).

---

## Step 2: Capture Baseline Screenshots

Before making any changes, capture screenshots of the current PF5 application state:

1. Start the development server for the application
2. Use the Chrome MCP server to navigate to key pages/routes
3. Take screenshots of each page and save them for comparison
4. Document which URLs were captured

Store baseline information for later comparison.

---

## Step 3: Fetch and Apply the PatternFly 6 Upgrade Guide

Fetch the official PatternFly 6 upgrade documentation:

1. Navigate to https://www.patternfly.org/get-started/upgrade/
2. Read and understand the upgrade steps, breaking changes, and migration patterns
3. Identify which changes apply to this codebase

Key areas to address from the upgrade guide typically include:
- Package updates (`@patternfly/react-core`, `@patternfly/react-icons`, etc.)
- CSS/SCSS changes and design token updates
- Component API changes (renamed props, removed components, new patterns)
- Import path changes

---

## Step 4: Perform the Migration

Apply the migration changes systematically:

1. **Update dependencies**: Update package.json with PF6 versions
2. **Run codemods**: If PatternFly provides migration codemods, run them
3. **Fix imports**: Update import paths as needed
4. **Update component usage**: Fix deprecated props and components
5. **Update styles**: Migrate CSS/design tokens

After each significant change:
- Ensure the application builds without errors
- Ensure TypeScript/linting passes

---

## Step 5: Visual Comparison Loop

This is the core verification step. Repeat until all pages match or you've exhausted fixes:

### 5.1 Capture Post-Migration Screenshots

1. Start the development server with the migrated code
2. Use Chrome MCP to navigate to the same URLs captured in Step 2
3. Take new screenshots of each page

### 5.2 Compare Screenshots

For each page, visually compare the baseline (PF5) screenshot with the current (PF6) screenshot:

1. Look for visual differences:
   - Layout shifts or misalignments
   - Color differences
   - Missing or broken components
   - Typography changes
   - Spacing issues
   - Icon differences

2. Document any differences found

### 5.3 Fix Visual Differences

For each visual difference:

1. Identify the root cause (CSS change, component change, prop change, etc.)
2. Consult the upgrade guide for the correct PF6 approach
3. Make the fix
4. Rebuild and verify

### 5.4 Repeat Until Matching

Continue the compare-fix loop until:
- All pages visually match the baseline (SUCCESS), OR
- You've attempted fixes but differences persist after 5 iterations (ESCALATE)

---

## Step 6: Final Verification

Once visual comparison passes:

1. Run the full test suite (if available)
2. Run linting and type checking
3. Do a final visual sweep of all captured pages
4. Commit all changes with a descriptive message:

```bash
git add -A
git commit -m "feat: Migrate from PatternFly 5 to PatternFly 6

- Updated all @patternfly/* packages to v6
- Fixed component API changes per upgrade guide
- Verified visual parity with original PF5 implementation

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Error Handling

### If Chrome MCP is unavailable
Stop immediately and inform the user. Do not proceed with migration.

### If visual differences cannot be resolved
After 5 fix attempts on the same issue:

1. Document the specific visual difference
2. Document what was tried
3. Ask the user how to proceed:
   - Accept the visual difference as expected PF6 behavior
   - Provide guidance on how to fix
   - Abort the migration

### If the application fails to build
1. Check build errors for PF6-specific issues
2. Consult the upgrade guide
3. If stuck, report the specific error to the user

---

## Completion Criteria

The migration is complete when:

- [ ] Chrome MCP server availability was verified
- [ ] Migration branch was created
- [ ] Baseline screenshots were captured
- [ ] PatternFly 6 upgrade guide was consulted
- [ ] Dependencies were updated to PF6
- [ ] All visual differences have been resolved (or explicitly accepted)
- [ ] Application builds without errors
- [ ] TypeScript/linting passes
- [ ] Changes are committed

---

## Tips

- Take screenshots at multiple viewport sizes if responsive design is important
- Focus on component-heavy pages first as they're most likely to have issues
- The PatternFly upgrade guide is authoritative - prefer its recommendations over other sources
- Some visual differences may be intentional PF6 design changes - these can be accepted after user confirmation
