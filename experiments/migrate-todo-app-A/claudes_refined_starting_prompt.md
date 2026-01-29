# PatternFly 5 to 6 Migration - Research and Planning Prompt

## Objective
Research the PatternFly 6 upgrade process and create a detailed migration plan for the todo-app application (currently on PatternFly 5). The migration plan must be broken into discrete units of work suitable for execution by an AI agent in the Ralph Agent workflow format.

## Phase 1: Research PatternFly 6 Upgrade Documentation

### Task 1.1: Fetch Official Upgrade Guide
- URL: https://www.patternfly.org/get-started/upgrade
- Extract comprehensive information on:
  - Breaking changes between PatternFly 5 and 6
  - Deprecated components and their PatternFly 6 replacements
  - API changes for components (props, interfaces, exports)
  - CSS/styling changes and class name updates
  - Migration strategies, codemods, and automated tools
  - Step-by-step manual upgrade instructions
  - Common gotchas, pitfalls, and troubleshooting

### Task 1.2: Research Additional Resources
- Check for PatternFly 6 migration codemods or CLI tools
- Look for breaking changes documentation
- Search for component-specific migration guides
- Review PatternFly 6 release notes and changelogs

### Task 1.3: Document Research Findings
Create a file: `patternfly-6-research.md` in the current directory containing:
- Summary of all breaking changes
- Component migration matrix (PF5 component → PF6 component + changes required)
- Styling/theming changes
- Dependency updates required
- Recommended migration approach (big bang vs incremental)
- Links to all relevant documentation

## Phase 2: Explore the Todo-App Codebase

### Task 2.1: Analyze Dependencies
- Read `todo-app/package.json` to identify:
  - Current PatternFly version (expect @patternfly/react-core ~5.x)
  - All PatternFly-related dependencies
  - React version (ensure compatibility with PF6)
  - Build tools (webpack, vite, etc.)

### Task 2.2: Map PatternFly Component Usage
- Search for all imports from `@patternfly/react-core`
- Search for all imports from `@patternfly/react-icons`
- Search for all imports from `@patternfly/react-styles`
- Create an inventory of:
  - Which components are used (Button, Form, Table, etc.)
  - Where they are used (file paths)
  - How they are configured (props, variants)

### Task 2.3: Identify Custom Styling
- Look for:
  - Custom CSS files that may reference PatternFly classes
  - CSS-in-JS that uses PatternFly tokens
  - Theme overrides or customizations
  - PatternFly CSS variables being used

### Task 2.4: Understand Application Structure
- Identify key directories and files:
  - Main entry point
  - Component organization
  - Routing structure
  - State management approach
- Document the architecture for context

## Phase 3: Create Migration Plan in Ralph Agent Format

### Task 3.1: Create prd.json
Create a `prd.json` file in the current directory with:
```json
{
  "projectName": "PatternFly 6 Migration - Todo App",
  "branchName": "feat/migrate-patternfly-6",
  "description": "Migrate todo-app from PatternFly 5 to PatternFly 6",
  "userStories": [
    // Stories to be defined based on research
  ]
}
```

### Task 3.2: Define User Stories
Break the migration into discrete user stories (each completable in <100k tokens):

**Story Structure Template:**
```json
{
  "id": "PF6-001",
  "title": "[Specific migration task]",
  "description": "Detailed description with:\n- Files to modify\n- Components to update\n- Expected changes\n- Verification steps",
  "acceptanceCriteria": [
    "All TypeScript errors resolved",
    "All linting errors resolved",
    "Application builds successfully",
    "No console errors in browser",
    "[Component-specific criteria]"
  ],
  "priority": 1,
  "passes": false
}
```

**Recommended Story Breakdown Pattern:**
1. **PF6-001**: Update dependencies (package.json + install)
2. **PF6-002**: Run codemods if available (automated transformation)
3. **PF6-003**: Update [ComponentType1] components (e.g., all Button/Link components)
4. **PF6-004**: Update [ComponentType2] components (e.g., all Form components)
5. **PF6-005**: Update [ComponentType3] components (e.g., all Table/List components)
6. **PF6-006**: Update styling and CSS class references
7. **PF6-007**: Update imports and module paths
8. **PF6-008**: Fix TypeScript type errors
9. **PF6-009**: Update tests to match new component APIs
10. **PF6-010**: Final verification and smoke testing

**Important:** Each story should:
- Be independently testable (can run `npm run typecheck` and `npm run lint`)
- Include specific file paths discovered during exploration
- Include detailed before/after code examples based on PF6 research
- Reference the research documentation for guidance

### Task 3.3: Create progress.txt Template
Create `progress.txt` with:
```
# PatternFly 6 Migration - Progress Log

## Codebase Patterns
(This section will be populated as patterns are discovered during migration)

---
```

## Phase 4: Create Research Documentation Output

### Task 4.1: Write patternfly-6-research.md
Comprehensive research document including:
- Executive summary of migration effort
- Detailed breaking changes
- Component-by-component migration guide
- Code examples (PF5 → PF6)
- Troubleshooting section
- Resources and links

### Task 4.2: Create Migration Checklist
A quick-reference checklist in the research doc:
- [ ] Dependencies updated
- [ ] Codemods run (if applicable)
- [ ] Component APIs updated
- [ ] Imports/exports updated
- [ ] Styling/CSS updated
- [ ] TypeScript errors resolved
- [ ] Tests updated
- [ ] Build passing
- [ ] Browser testing completed

## Execution Guidelines

### Quality Standards
- All user stories must be verifiable (typecheck, lint, build, test)
- Each story must be atomic and focused
- Include rollback information for each story
- Document learnings in progress.txt after each story

### Tools to Use
- **Glob**: Find all files using PatternFly components (`**/*.tsx`, `**/*.jsx`)
- **Grep**: Search for specific component imports and usage patterns
- **Read**: Examine package.json, components, and configuration
- **WebFetch**: Pull latest PatternFly 6 documentation as needed
- **WebSearch**: Find additional migration resources if documentation is unclear

### Output Files Expected
After completing this prompt, you should have created:
1. `patternfly-6-research.md` - Comprehensive upgrade research
2. `prd.json` - User stories in Ralph Agent format
3. `progress.txt` - Progress log template
4. (Optional) `migration-notes.md` - Any additional context for executors

## Success Criteria
- ✅ PatternFly 6 upgrade process thoroughly researched and documented
- ✅ Todo-app codebase fully explored and PatternFly usage mapped
- ✅ Migration plan created with 8-15 discrete, executable user stories
- ✅ Each user story contains detailed instructions with file paths and code examples
- ✅ All output files created and ready for Ralph Agent execution
- ✅ Each story is scoped to be completable in <100k tokens

## Next Steps After This Prompt
Once research and planning are complete, a Ralph Agent will execute the migration by:
1. Checking out branch `feat/migrate-patternfly-6`
2. Iteratively completing each user story where `passes: false`
3. Running quality checks after each story
4. Committing with format: `feat: [Story ID] - [Story Title]`
5. Updating prd.json to mark stories as `passes: true`
6. Logging progress and learnings to progress.txt
