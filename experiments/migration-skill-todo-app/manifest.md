# UI Manifest

Project: /Users/pgaikwad/Projects/00_analysis_apps/nodejs/todo-app

## Routes

| Route | Screenshot | Notes |
|-------|------------|-------|
| / | dashboard.png | Main dashboard page with stats and quick actions |
| /todos | todolist.png | Full TODO list with filtering and sorting |

## Interactive Components

| Type | Name | Screenshot | Trigger |
|------|------|------------|---------|
| Modal | Create TODO | modal-create-todo.png | Click "Create TODO" button on dashboard or todolist |
| Modal | Edit TODO | modal-edit-todo.png | Click edit icon on a TODO in the list |
| Modal | Delete Confirmation | modal-delete-confirm.png | Click delete icon on a TODO in the list |
| Form | Quick Create TODO | form-quick-create.png | Click "Expand to Create" button on dashboard |
| Dropdown | Priority Filter | dropdown-priority.png | Click priority filter on TODO list page |
| Dropdown | Color Filter | dropdown-color.png | Click color filter on TODO list page |

## Key Components Per Page

### / (Dashboard)
- AppNav navigation bar (Dashboard and TODO List buttons)
- Stats cards row (Total TODOs, Overdue TODOs, Completed Today)
- Overdue TODOs section with data list
- Quick Create TODO section (expandable form)

### /todos (TODO List)
- AppNav navigation bar
- Filter bar (Priority dropdown, Color dropdown, Show Overdue Only toggle, Clear filters)
- Sortable table with TODO items
- Checkboxes for marking complete
- Edit and Delete action buttons per row

## Navigation Elements

| Element | Screenshot | Notes |
|---------|------------|-------|
| AppNav | appnav.png | Present on all pages with Dashboard and TODO List buttons |
