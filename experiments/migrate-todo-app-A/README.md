# Overview

First experiment using a Ralph loop to do a Patternfly 5->6 migration.

## Initial prompt

        Your job is to create a prompt in markdown and write it to the current working directory with the best name you see for claude code to use in future.  Ask me any clarifying questions you need to improve this prompt in a serial nature.  I want you to help me migrate the patternfly 5 application under the "todo-app" application to patternfly 6. Patternfly 6 upgrade documentation is located at https://www.patternfly.org/get-started/upgrade.  Your first task is to research how to upgrade to patternfly 6 from 5 and to record your research in markdown documents to guide later execution.  Be as thorough as possible in researching migration guidance.  Next inspect the application and consider based on what you know what the upgrade steps will be to address to move to patternfly 6.  Develop a migration plan to move to patternfly 6.  Break the plan down into discrete units of work that are easily accomplished by an AI agent under 100k tokens per session.  This migration plan is intended to be executed by an ai agent in a subsequent loop.
        
        
        - Would you like the research documentation and migration plan in a single file or separate files? → Separate files - research and plan split
        - Should the migration plan be formatted to work with the existing Ralph Agent workflow (prd.json + progress.txt)? → Yes - use Ralph Agent format (Recommended)
        - What level of detail do you want for each migration step? → Detailed instructions (Recommended)
                
        Please write your prompt to disk, we will conduct research and execution in a follow up step

## PRD skill improved prompt to
[prd-patternfly-6-migration.md](prd-patternfly-6-migration.md)

## Thoughts to improve
- Have the agent conduct research for the migration process from best practices and docs
- Include the research in a skill that is geared towards analyzing an app and generating a migration plan
- Allow the skill to break the migration plan out into sufficiently scoped tasks so they can executed and verified in a single iteration of a ralph loop (i.e keep context to ~<50% of the models context window, guidance is ~100k for Opus, ~500k for Sonnet>)
- Allow the skill the execute the migration plan and verify each step
- Allow the skill to perform a visual regression test on the major screens of the app

## Result of experiment
* See: [./sample_run_output.txt](./sample_run_output.txt)
* See: https://github.com/jwmatthews/mig-demo-apps/pull/2/changes
* See: [./after_migration.png](./after_migration.png)
