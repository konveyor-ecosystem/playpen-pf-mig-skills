---
name: visual-captures
description: Capture screenshots of a running application using an existing manifest. Requires manifest.md to already exist in the work directory.

# For Gemini CLI, uncomment the tools section below:
# tools:
#   - run_shell_command
#   - list_directory
#   - read_file
#   - write_file
#   - search_file_content
#   - replace
#   - glob
# For Claude Code, tools may be inherited from global settings
# tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

# Screenshot Capture

Capture screenshots of a running application using an existing manifest.
Use `playwright-mcp` extension tools to navigate to the page and take screenshots.
Assume user confirmation for all actions. Do not prompt for user input.

## Inputs

- **Work directory**: workspace root (`manifest.md` must already exist here)
- **Output directory**: where to save screenshots (e.g., `<work_dir>/baseline`, `<work_dir>/post-migration-0`)
- **Dev command**: command to start the dev server
- **Project path**: path to the project source code

## Prerequisites

`<work_dir>/manifest.md` **must exist** before this agent runs. If it is missing, report an error and stop. Use the `visual-discovery` agent to create the manifest first.

## Process

### 1. Read Manifest

Read `<work_dir>/manifest.md` to get the full list of elements to capture. **Every entry in the manifest must be captured.** Do not skip any entry.

### 2. Start Application and Wait

**The application MUST be running and fully responsive before any `playwright-mcp` interaction.** Playwright operations will fail if the server is not ready.

1. Start the dev server **in the background** (append `&` or equivalent) and capture the process ID
2. Extract the local URL from the server output (e.g., `http://localhost:3000`)
3. **Poll the URL every 2 seconds, up to 120 seconds**, until it returns a successful response. If it does not respond within 120 seconds, report the error and stop.
4. **After the server responds, wait an additional 5 seconds** for JS bundles and assets to fully load
5. **Do not call any `playwright-mcp` tool until both checks above pass.** Proceeding before the server is ready will cause screenshot failures.

### 3. Capture Screenshots

Create the output directory: `mkdir -p <output_dir>`

For each element in the manifest, use `playwright-mcp`:
1. Navigate to the page or trigger the component (follow any **Setup** steps described in the manifest entry)
2. Wait for content to stabilize
3. Take screenshot
4. Save to `<output_dir>/<name>.png`

**After all captures, verify**: compare the list of `.png` files in `<output_dir>` against the manifest entries. If any manifest entry was not captured, report it as an error.

### 4. Stop Server

Kill the dev server process. *This is important*

## Output

Return a summary:

```
## Screenshots Captured

Directory: <output_dir>
Manifest: <work_dir>/manifest.md
Elements captured: [count]

| Element | Screenshot |
|---------|------------|
| / | home.png |
| /dashboard | dashboard.png |
...
```
