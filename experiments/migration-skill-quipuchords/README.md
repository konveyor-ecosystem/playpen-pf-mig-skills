# Overview
This directory contains the run of an experiment to migrate a specific application from PatternFly 5 to PatternFly 6.
* Application to migrate: https://github.com/quipucords/quipucords-ui
  * We will use the tag `2.1.0` which was the last release prior to migrating to PF 6.
    * https://github.com/quipucords/quipucords-ui/releases/tag/2.1.0
  * `quipucords-ui` was chosen so we can compare the output of the AI generated migration from what an experienced PatternFly developer completed in 
    * https://github.com/quipucords/quipucords-ui/pull/664

This specific run is using `goose` and a migration recipe from [../../goose/recipes](../../goose/recipes/migration.yaml)
## Setup
### Install Goose
1. Download Goose <= 1.24.0 from https://github.com/block/goose/releases
  * Note: There is a bug with the new summon extension in 1.25.0 when using recipes with subagents and we need to test the workaround better to confirm it fixes the problem until there is an updated version.
2. Extract it and place it in your path.

Install Kantra
Download and extract kantra .zip from https://github.com/konveyor/kantra/releases
Extract the archive and place the kantra binary in your path
Move the rest of the contents to ~/.kantra
Todo:  Consider if we should update to use the rules Pranav updated at https://github.com/pranavgaikwad/rulesets/tree/enhancePf6Rules/stable/nodejs/patternfly
GCP Test Script (Optional but helpful to confirm credentials)
Download and save the script in your path https://gist.github.com/jwmatthews/b21caa835a6efd05da023b44b8bd6ac8
Setup
Goose with GCP Vertex AI
Run the GCP test script to confirm you are logged into GCP Vertex AI and ensure you have the environment variables exported:
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=
Use Claude GCP Project - Global Engineering Teams, Product, IT and Sales to locate your project ID
More extensive Claude Code Install Instructions

Run goose configure
Select Configure Providers
Select GCP Vertex AI
Enter your project ID when prompted for the GCP_PROJECT_ID
Enter us-east5 when prompted for GCP_LOCATION
Enter the desired model, for example claude-opus-4-6 by choosing Enter a model no listed, if you want to use one not listed.
When done goose will exit
Goose Playwright MCP Server
Run goose configure again
Select Add Extension
Select Command-line Extension
Enter a playwright for the name
Enter npx -y @playwright/mcp@latest for the command
Enter 300 for the timeout
Enter Playwright MCP Server for the description
Choose No when prompted to set environment variables
Goose Developer Tools
Run goose configure again
Select Add Extension
Select Built-in Extension
Select  Developer Tools
Enter 300 for the timeout
Run
Run the Migration Harness
Clone https://github.com/konveyor-ecosystem/playpen-pf-mig-skills
Clone the source repo to migrate. Examples
https://github.com/quipucords/quipucords-ui 
https://github.com/pranavgaikwad/mig-demo-apps
Revert the repo to a pre patternfly 6 state if necessary
71caf759b43fe294e54d75b27db4ffc35f108498 for quipucords-ui

Change directory cd playpen-pf-mig-skills to prepare running migration
Run goose, for example:
goose run --recipe goose/recipes/migration.yaml \
--params source_tech="PatternFly 5" \
--params target_tech="PatternFly 6" \
--params input_path="/home/jmontleo/Documents/src/github.com/konveyor/mig-demo-apps/kai/nodejs/todo-app" \
--params workspace_dir="/tmp/todo-migration" \
--params rules="/home/jmontleo/.kantra/rulesets/nodejs/patternfly/" \
--interactive

Enter a prompt, for example: Migrate the application specified by input_path from Patternfly 5 to Patternfly 6 and the migration will begin.


### Run

## Results
