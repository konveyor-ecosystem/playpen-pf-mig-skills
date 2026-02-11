---
name: visual-baseline
description: Discover UI components and capture screenshots. Creates manifest on first run, reuses it on subsequent runs.

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

Discover UI components and capture screenshots of a running application.
Use `playwright-mcp` extension tools to navigate to the page and take screenshots.
Assume user confirmation for all actions. Do not prompt for user input.

## Inputs

- **Work directory**: workspace root (`manifest.md` lives here)
- **Output directory**: where to save screenshots (e.g., `<work_dir>/baseline`, `<work_dir>/post-migration-0`)
- **Dev command**: command to start the dev server
- **Project path**: path to the project source code

## Process

### 1. Check for Manifest

If `<work_dir>/manifest.md` exists, skip to step 3.

If it does NOT exist, proceed to step 2.

### 2. Discover All Important UI Elements

Only run if manifest does not exist.

**Find ALL important UI elements.** This includes more than just routes:

**Routes/Pages:**
- Search for router config, route arrays, path definitions
- Check `pages/`, `views/`, `routes/`, `screens/` folders
- Find menus, sidebars, navbars and extract all links

**Interactive Components (not tied to routes):**
- **Modals/Dialogs** - Search for Modal, Dialog, Popup components and find their triggers
- **Drawers/Sidepanels** - Slide-out panels triggered by buttons
- **Forms** - Important forms in modals or triggered by actions
- **Dropdowns/Menus** - Complex dropdown menus with multiple options
- **Tabs** - Tab panels with distinct content
- **Accordions** - Expandable sections with hidden content

**Do not skip any discoverable element.** For each interactive component, note:
- What triggers it (button click, hover, etc.)
- What state/data it needs to appear

Create `<work_dir>/manifest.md`:

```markdown
# UI Manifest

Project: <project_path>

## Routes

| Route | Screenshot | Notes |
|-------|------------|-------|
| / | home.png | |
| /dashboard | dashboard.png | |
| /settings | settings.png | Requires mock auth |

## Interactive Components

| Type | Name | Screenshot | Trigger |
|------|------|------------|---------|
| Modal | Confirm Delete | modal-confirm-delete.png | Click delete button on /dashboard |
| Drawer | Settings | drawer-settings.png | Click gear icon |
| Form | Create User | form-create-user.png | Click "Add User" on /users |

## Key Components Per Page

### /dashboard
- Sidebar navigation
- Stats cards row
- Data table with action buttons
```

**Naming convention:**
- Routes: `/` → `home.png`, `/dashboard` → `dashboard.png`
- Modals: `modal-confirm-delete.png`, `modal-create-user.png`
- Drawers: `drawer-settings.png`
- Forms: `form-login.png`

### 3. Start Application and Wait

**Run the dev server in the background** and determine the URL from its output:

1. Start the dev server command **in the background** (append `&` or equivalent)
2. Observe the output to find the local URL (e.g., `http://localhost:3000`)
3. Wait for the server to respond (poll every second, up to 120 seconds)
4. After server responds, wait additional 5 seconds for JS/assets to load
5. **Do not proceed until server is ready.** If it doesn't start, report error and stop.

### 4. Capture Screenshots

Create the output directory: `mkdir -p <output_dir>`

Read `<work_dir>/manifest.md`. For each element listed, use `playwright-mcp`:
1. Navigate to the page or trigger the component
2. Wait for content to stabilize
3. Take screenshot
4. Save to `<output_dir>/<name>.png`

### 5. Stop Server

Kill the dev server process.

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
