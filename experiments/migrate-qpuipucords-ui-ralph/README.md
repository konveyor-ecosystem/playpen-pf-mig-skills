# Overview
This directory captures an experiment of running a simple "ralph.sh" loop with minimal guidance to migrate https://github.com/quipucords/quipucords-ui from PF 5 to PF 6.
We are choosing this as a sample since we have a PR identified that shows the result of a PF 6 migration manually completed.

## Source application to migrate
* PatternFly developers helped to migrate the codebase from PF 5 to PF 6 in below PR:
  *  [feat(pf6): upgrade UI to PatternFly 6
#664](https://github.com/quipucords/quipucords-ui/pull/664)
  * This implies that we can use an older commit to look at the PF 5 code base:
    * Looking at changes to package.json we can see that commit `6a8b6a7e9b65cf5aeeda4e12789737dd4ae0e706` is on PF 5
    * Tag 2.1.0 is last release on PF 5
  * We are using ```./checkout_source.sh``` to clone the repo and checkout the tag

## How was this experiment setup:
* Using claude code with Opus 4.6 (1M)

1. Start with a simple prompt in ```01_initial_starting_point.md``` and ask claude to use to create a prompt to begin the work.  
    ```
    Run the prompt in @01_initial_starting_point.md
      ⎿  Read 01_initial_starting_point.md (8 lines)

    ● I'll start by researching the PatternFly 6 upgrade documentation and inspecting the quipucords-ui application in parallel.

    ● 2 agents finished (ctrl+o to expand)
      ├─ Task (Research PF6 upgrade docs) · 35 tool uses · 34.5k tokens
      │  ⎿  Done
      └─ Explore (Explore quipucords-ui codebase) · 43 tool uses · 50.3k tokens
          ⎿  Done

    ```
      * Ran for 6 minutes
1. Claude asked a few clarifying questions
    ```

    Review your answers

    ● The quipucords-ui app already uses deprecated PF5 Select components (imported from `@patternfly/react-core/deprecated`). Should the migration plan include fully replacing these with the new composable Select/template API,
      or just move them to the PF6 deprecated path as a transitional step?
      → Full replacement (Recommended)
    ● The `/src/vendor/react-table-batteries/` directory contains forked/vendored code from tackle2-ui that wraps PatternFly table components and uses deprecated Select components. Should the AI agent migrate this vendor code
    as well, or should it be treated as out of scope?
      → Migrate vendor code too (Recommended)
    ● Should the migration plan include updating and fixing all 33 test files to pass after migration, or should test updates be a separate follow-up effort?
      → Include test fixes (Recommended)
    ● Should the migration plan target running the PF codemods (automated tools) as a first pass, or should the AI agent make all changes manually for more control?
      → Run codemods first (Recommended)
    ```
      * The above resulted in [02_migrate_quipucords_ui.md](./02_migrate_quipucords_ui.md)
  1. Run claude and use the PRD skill to improve 02_migrate_quipucords_ui.md 
      ```
      use the PRD skill to improve @02_migrate_quipucords_ui.md, write the improvement to 03_improved_prompt_prd.md
      
      ←  ☒ PRD Goal  ☒ Story sizing  ☒ Quality checks  ☒ Visual verify  ✔ Submit  →

      Review your answers

      ● What is the primary goal for the PRD structure?
        → Ralph JSON conversion
      ● Should the PRD preserve the exact 10-unit structure from the source document, or should stories be resized?
        → Keep 10 units as-is
      ● What quality checks should acceptance criteria reference?
        → All checks from source doc (Recommended)
      ● Should the PRD include browser/visual verification acceptance criteria?
        → Yes, include browser checks

        ⏺ The PRD has been written to 03_improved_prompt_prd.md. Here's what changed from the original document:

      Structural improvements:
      - Reorganized from a flat "units of work" document into a proper PRD with Introduction, Goals, User Stories (US-001 through US-010), Functional Requirements, Non-Goals, Technical Considerations, Success Metrics, and Open
      Questions
      - Each unit mapped to a user story with a description ("As a developer, I want...") and checkbox-style acceptance criteria that are programmatically verifiable
      - Added browser verification criteria to every UI-affecting story (US-002 through US-010)

      Content improvements:
      - Added explicit "Files to modify" lists on every story
      - Success metrics are concrete and measurable (specific commands that must exit 0, specific coverage thresholds)
      - Non-goals section clearly scopes the migration (no functional changes, no new features, no architecture changes)
      - Technical considerations section captures cross-cutting concerns (execution order, vendor code treatment, snapshot strategy, commit conventions)
      - Open questions section surfaces unknowns that should be investigated during US-001

      Ralph compatibility:
      - Structured for direct conversion to prd.json — each user story has a clear ID, title, description, and verifiable acceptance criteria
      - Stories are sequential with explicit ordering dependency noted
      - All quality check commands spelled out so an autonomous agent can run them
      ```
      * Resulted in [03_improved_prompt_prd.md](./03_improved_prompt_prd.md)
1. Run claude with the ralph skill to create a prd.json
      ```
      Use the ralph skill to create a prd.json from @03_improved_prompt_prd.md


      The prd.json has been written. Here's a summary of the conversion:

      Structure: 10 user stories (US-001 through US-010) mapped 1:1 from the PRD units, ordered by priority/dependency.

      Key decisions:
      - Branch: ralph/pf6-migration-quipucords-ui (Ralph convention)
      - All stories start with passes: false
      - Every story includes "npm run test:types passes" in acceptance criteria
      - Every UI story (US-002 through US-010) includes "Verify in browser using dev-browser skill"
      - Technical context (file lists, migration patterns, code examples) moved to the notes field to keep acceptance criteria concise and verifiable
      - Acceptance criteria are concrete and checkable — no vague "works correctly" statements

      Story dependency chain: strictly sequential (1→2→3→...→10). US-001 must run first (codemods), US-010 is final verification. Each story builds on the previous.
  ⎿  ```
      * Results in [prd.json](./prd.json)
