# Overview

This directory contains an example of using claude to conduct research on design tokens to explain to non-designers.  This was executed in a "ralph" loop.

## Explanation of how this was performed

1. Work with claude to ask it to create a prompt to guide the initial research process.

        Claude: Build a prompt using best practices that will research CSS Design Token migration as it relates to PatternFly 5 to 6 migrations. Read https://www.patternfly.org/get-started/upgrade for a starting point. Focus on the potential problem for a user to need to handle the gaps of CSS updates where the pf-codemods tool is unable to help. Research CSS Design Tokens and gather context of what they do and how they are used and how PatternFly 6 is using them. Write all your relevant research to individual markdown files when it makes sense so future operations have the context of what you learned. Understand the pain a user has with this migration, research what the typical customer journeys are and describe the most common scenarios. When you are done write your prompt in markdown as Prompt_research_css_design_tokens_patternfly_6.md

2. Claude: 
    
        Use the skill PRD to convert Prompt_research_css_design_tokens_patternfly_6.md into a PRD format, write the resulting markdown file to this working directory with a filename you think makes the most sense.

3. Claude: 

       Use the ralph skill to convert tasks/prd-css-design-token-research.md to a prd.json in this working directory

3. Run ralph.sh to invoke claude to execute the prd.json, tracking it's progress in progress.txt

      ```./ralph.sh --tool claude 10```

## Results
* See [research/00_executive_summary.md](research/00_executive_summary.md) to begin and other files in the [research](research) directory.
