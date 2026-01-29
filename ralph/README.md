# Overview
Basic pieces to enable running an AI agent in a "ralph" loop.
* See https://ghuntley.com/loop/ for an explanation of the concept

* These scripts originated from https://github.com/snarktank/ralph.
    * They have been copied to this example repo to ease tweaks as we explore usage of the ralph loop applied to our use-cases.
    * See: [../THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Instructions to use
1. ```cp -R skills/prd ~/.claude/skills```
2. ```cp -R skills/ralph ~/.claude/skills```
3. ```cd $WORKDIR```
   * This assumes that you have changed directory to wherever you want to work.
4. ```cp $PATH_TO_THIS_DIR/playpen-pf-mig-skills/ralph/CLAUDE.md .```
   * You will want the CLAUDE.md in this directory to be in your working directory to instruct claude.
5. ```cp $PATH_TO_THIS_DIR/playpen-pf-mig-skills/ralph/ralph.sh .```
6. Create a prompt that captures what you want to accomplish, let's call it prompt.md 
7. Run claude and ask it to "Use the PRD skill to convert prompt.md to a PRD document, name the PRD what you think is appropriate in this working directory."
8. Run claude and ask it to "Use the Ralph skill to convert the PRD document to a prd.json, write the prd.json in this working directory."
9. Now run the ralph loop (note this expects you are in your working directory, not the checkout of this git repo): ```./ralph.sh --tool claude 10```
