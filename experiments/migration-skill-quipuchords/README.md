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
1. Extract it and place it in your path.
1. Configure Providers for your environment

### Install Kantra
1. Download and extract kantra .zip from https://github.com/konveyor/kantra/releases
1. Extract the archive and place the kantra binary in your path
1. Move the rest of the contents to ~/.kantra
  * Note:  We are working through some updates to the analysis rules, latest rules we have are located here:
    * https://github.com/pranavgaikwad/rulesets/tree/enhancePf6Rules/stable/nodejs/patternfly

### Goose Playwright MCP Server
1. Run goose configure
1. Select Add Extension
1. Select Command-line Extension
1. Enter a playwright for the name
1. Enter npx -y @playwright/mcp@latest for the command
1. Enter 300 for the timeout
1. Enter Playwright MCP Server for the description
1. Choose No when prompted to set environment variables

### Goose Developer Tools
1. Run goose configure again
1. Select Add Extension
1. Select Built-in Extension
1. Select  Developer Tools
1. Enter 300 for the timeout

## Run
### Checkout the quipucords-ui repo
1. ```./checkout_src.sh```
  * This is an example of how we checked out the repo from a fork, adjust as you'd like

### Checkout the updated analysis rules
1. ```./checkout_rules.sh```
  * This includes the latest rules in https://github.com/pranavgaikwad/rulesets/tree/enhancePf6Rules/stable/nodejs/patternfly

### Run the Migration Harness
1. ```./goose.sh```
  * Consider running this in a VM if you want to protect against inadvertent changes
    * Note:  This will take on the order of ~2-3 hours to complete
    * The output will go to a migration-$DATETIME.log and the terminal

## Results
* Output of the harness running
  * You can look at [migration-20260224-144635.log](./migration-20260224-144635.log) for an example of a full run
* The migration harness writes artifacts to the [workdir](./workdir) directory

### Migration Report
* A migration report was produced under [workdir/report.html](./workdir/report.html)
  * This is also viewable from:  https://exuberant-fiction.surge.sh/report.html

### Quipuchords UI Branch with code changes
* The migration began on the ```2.1.0``` tag of https://github.com/quipucords/quipucords-ui/releases/tag/2.1.0
* The code was stored in the Fork + Branch at: https://github.com/jwmatthews/quipucords-ui/tree/pf6_mig_skill_try3
  * A PR was generated to the fork against 2.1.0 to help with reviewing the changes:
    * https://github.com/jwmatthews/quipucords-ui/pull/3
