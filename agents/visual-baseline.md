---
name: visual-baseline
description: Capture baseline screenshots of all important pages before migration. Use in pre-migration phase for UI migrations.
---

# Visual Baseline Capture

Capture baseline screenshots before migration begins.

## Inputs

You receive:
- **Work directory**: where to store screenshots
- **Dev command**: command to start the dev server
- **Project path**: path to the project source code

## Process

### 1. Discover Pages

Find ALL important pages using multiple methods:
- Search code for route definitions
- Look in `pages/`, `views/`, `routes/` folders
- Check navigation menus and sidebars in code
- Identify modals, drawers, tabs with distinct content

Create a list of routes to capture. If pages require auth/data, note if you can mock them.

### 2. Start Application and Wait

**Run the dev server in the background** and determine the URL from its output:

1. Start the dev server command **in the background** (append `&` or equivalent)
2. Observe the output to find the local URL (e.g., `http://localhost:3000`)
3. Wait for the server to respond (poll every second, up to 120 seconds)
4. After server responds, wait additional 5 seconds for JS/assets to load
5. **Do not proceed until server is ready.** If it doesn't start, report error and stop.

### 3. Capture Screenshots

Create baseline directory: `<work_dir>/baseline/`

For each route, use `playwright-mcp`:
1. `browser_navigate` to `<app_url><route>`
2. Wait for page to stabilize (network idle)
3. `browser_take_screenshot`
4. Save to `<work_dir>/baseline/<route-name>.png`

**Naming convention:**
- `/` → `home.png`
- `/dashboard` → `dashboard.png`
- `/settings/profile` → `settings-profile.png`

### 4. Stop Server

Kill the dev server process.

### 5. Create Manifest

Create `<work_dir>/baseline/manifest.md`:

```markdown
# Visual Baseline

Captured: <timestamp>
Project: <project_path>
App URL: <app_url>

## Pages

| Route | Screenshot | Notes |
|-------|------------|-------|
| / | home.png | |
| /dashboard | dashboard.png | |
| /settings | settings.png | Requires mock auth |
```

## Output

Return a summary:

```
## Baseline Capture Complete

Directory: <work_dir>/baseline
Pages captured: [count]

| Route | Screenshot |
|-------|------------|
| / | home.png |
| /dashboard | dashboard.png |
...

Manifest: <work_dir>/baseline/manifest.md
```
