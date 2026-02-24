# UI Manifest

Project: ./quipucords-ui

## Routes

### /credentials → credentials.png
- **Navigate to**: `/credentials` (also the default redirect from `/`)
- **Wait for**: credentials table to fully render, toolbar visible
- **Key elements**: sidebar navigation (Credentials active), toolbar with filter, "Add Credential" dropdown, Delete button, refresh button, pagination, data table with columns: Name, Type, Authentication Type, Sources, Last Updated, Actions (kebab)
- **Notes**: requires login (see Authentication section)

### /sources → sources.png
- **Navigate to**: `/sources`
- **Wait for**: sources table to fully render, toolbar visible
- **Key elements**: sidebar navigation (Sources active), toolbar with filter, "Add Source" dropdown, Scan button, Delete button, refresh button, pagination, data table with columns: Name, Last Completed, Type, Credentials, Scan button, Actions (kebab)
- **Notes**: requires login

### /scans → scans.png
- **Navigate to**: `/scans`
- **Wait for**: scans table to fully render, toolbar visible
- **Key elements**: sidebar navigation (Scans active), toolbar with filter, Delete button, refresh button, pagination, data table with columns: Name, Last Scanned, Sources, Actions (kebab with Summary/Delete/Rescan/Download)
- **Notes**: requires login

### /not-found → not-found.png
- **Navigate to**: any invalid path (e.g., `/invalid-route`)
- **Wait for**: empty state to render
- **Key elements**: ExclamationTriangleIcon, "404 Page Not Found" title, description text, "Take me home" button

### Login page → login.png
- **Navigate to**: `/` (when not authenticated)
- **Wait for**: login form to render
- **Key elements**: PatternFly LoginPage with username field, password field, "Log in" button, error alert area, brand/logo

## Interactive Components

### Modal: Add Credential (Username/Password type) → modal-add-credential.png
- **Trigger**: on `/credentials`, click "Add Credential" dropdown, then select "Network"
- **Wait for**: modal to appear with form fields
- **Key elements**: modal title "Add credential: Network", Name field, Authentication Type dropdown (Username and Password / SSH Key), Username field, Password field, Become Method dropdown, Become User field, Become Password field, Save/Cancel buttons

### Modal: Add Credential (Token type) → modal-add-credential-token.png
- **Trigger**: on `/credentials`, click "Add Credential" dropdown, then select "OpenShift"
- **Wait for**: modal to appear with form fields
- **Key elements**: modal title "Add credential: OpenShift", Name field, Authentication Type dropdown (Token / Username and Password), Token field, Save/Cancel buttons
- **Notes**: representative of token-based credential types (OpenShift, RHACS)

### Modal: Confirm Delete Credential → modal-delete-credential.png
- **Trigger**: on `/credentials`, click kebab menu on a credential row (one without associated sources), then click "Delete"
- **Wait for**: confirmation modal to appear
- **Key elements**: modal title with delete confirmation, credential name in message, Delete (danger) button, Cancel button

### Modal: View Sources (from credential row) → modal-credential-sources.png
- **Trigger**: on `/credentials`, click the sources count link on a credential row that has sources
- **Wait for**: modal with list to appear
- **Key elements**: modal title "Sources", bordered plain list of source names, Close button

### Modal: Add Source (Network type) → modal-add-source-network.png
- **Trigger**: on `/sources`, click "Add Source" dropdown, then select "Network"
- **Wait for**: modal to appear with form fields
- **Key elements**: modal title "Add Source: Network", Name field, Credentials typeahead-checkbox multi-select, Search addresses textarea, Port field, Paramiko checkbox, Save/Cancel buttons

### Modal: Add Source (Non-network type) → modal-add-source-openshift.png
- **Trigger**: on `/sources`, click "Add Source" dropdown, then select "OpenShift"
- **Wait for**: modal to appear with form fields
- **Key elements**: modal title "Add Source: OpenShift", Name field, Credentials single-select, IP address/hostname field, Port field (default 6443), Proxy URL field, Connection SSL protocol dropdown, SSL verify checkbox, Save/Cancel buttons
- **Notes**: representative of non-network source types (OpenShift, Satellite, vCenter, RHACS, Ansible)

### Modal: Confirm Delete Source → modal-delete-source.png
- **Trigger**: on `/sources`, click kebab menu on a source row (one without active connections), then click "Delete"
- **Wait for**: confirmation modal to appear
- **Key elements**: modal title with delete confirmation, source name in message, Delete (danger) button, Cancel button

### Modal: View Credentials (from source row) → modal-source-credentials.png
- **Trigger**: on `/sources`, click the credentials count link on any source row
- **Wait for**: modal with list to appear
- **Key elements**: modal title "Credentials", bordered plain list of credential names, Close button

### Modal: Show Connections → modal-show-connections.png
- **Trigger**: on `/sources`, click the connection status link on a source row that has a completed connection
- **Wait for**: modal to appear with expandable table
- **Key elements**: modal title (source name), expandable table with three sections: Failed connections (danger icon), Unreachable systems (warning icon), Successful connections (success icon), Close button

### Modal: Scan Sources → modal-scan-sources.png
- **Trigger**: on `/sources`, click "Scan" button on a source row
- **Wait for**: modal to appear with scan form
- **Key elements**: modal title "Scan", Name field, Sources textarea (disabled, pre-filled), Maximum concurrent scans number input, Deep scan checkboxes (JBoss EAP, Fuse, JBoss web server), Save/Cancel buttons

### Modal: Confirm Delete Scan → modal-delete-scan.png
- **Trigger**: on `/scans`, click kebab menu on a scan row, then click "Delete"
- **Wait for**: confirmation modal to appear
- **Key elements**: modal title with delete confirmation, scan name in message, Delete (danger) button, Cancel button

### Modal: View Sources (from scan row) → modal-scan-sources-list.png
- **Trigger**: on `/scans`, click the sources count link on any scan row
- **Wait for**: modal with list to appear
- **Key elements**: modal title "Sources", bordered plain list of source names, Close button

### Modal: Show Scan Jobs → modal-show-scan-jobs.png
- **Trigger**: on `/scans`, click the last scanned status link on a scan row that has completed jobs
- **Wait for**: modal to appear with scan jobs table
- **Key elements**: modal title with scan name, count of scans that have run, sortable table with columns: Scan Time, Scan Result, Download button, Close button

### Modal: Aggregate Report Summary → modal-aggregate-report.png
- **Trigger**: on `/scans`, click kebab menu on a scan row with a completed report, then click "Summary"
- **Wait for**: modal to appear with description list
- **Key elements**: modal title "Scan Summary", subtitle with scan ID, horizontal compact description list with stats (ansible hosts, hypervisor instances, physical instances, etc.), Close button

### Modal: About → modal-about.png
- **Trigger**: click the help (?) icon in the masthead toolbar, then click "About"
- **Wait for**: PatternFly AboutModal to appear
- **Key elements**: brand logo, user info, browser details, UI version, server version, CPU architecture, close button

### Dropdown: Add Credential → dropdown-add-credential.png
- **Trigger**: on `/credentials`, click "Add Credential" button
- **Wait for**: dropdown menu to appear
- **Key elements**: dropdown items: Network, OpenShift, RHACS, Satellite, vCenter, Ansible

### Dropdown: Add Source → dropdown-add-source.png
- **Trigger**: on `/sources`, click "Add Source" button
- **Wait for**: dropdown menu to appear
- **Key elements**: dropdown items: Network, OpenShift, RHACS, Satellite, vCenter, Ansible

### Dropdown: Action Menu (kebab) → dropdown-action-menu.png
- **Trigger**: on `/credentials`, click the kebab (⋮) menu on any credential row
- **Wait for**: dropdown menu to appear
- **Key elements**: Edit and Delete menu items
- **Notes**: representative of all kebab action menus across views

### Dropdown: User Menu → dropdown-user-menu.png
- **Trigger**: click the user dropdown in the masthead toolbar
- **Wait for**: dropdown menu to appear
- **Key elements**: Logout option

### Dropdown: Help Menu → dropdown-help-menu.png
- **Trigger**: click the help (?) icon in the masthead toolbar
- **Wait for**: dropdown menu to appear
- **Key elements**: About option

## Theme/Layout Variants

### /credentials (dark theme) → credentials--dark.png
- **Navigate to**: `/credentials`
- **Setup**: click the dark theme toggle (moon icon) in the masthead toolbar's ToggleGroup
- **Wait for**: theme class `pf-v5-theme-dark` to be applied, layout to settle
- **Key elements**: same as credentials.png but with dark theme applied to masthead, sidebar, and content area

### /credentials (sidebar collapsed) → credentials--sidebar-collapsed.png
- **Navigate to**: `/credentials`
- **Setup**: click the hamburger menu button (NavToggle) in the masthead to collapse the sidebar
- **Wait for**: sidebar to collapse, content area to expand
- **Key elements**: collapsed sidebar (no text labels visible), expanded content area with credentials table

## Authentication

- **Login required**: YES
- **Login page**: PatternFly LoginPage rendered when not authenticated
- **Credentials**: Check `.env`, `README`, or test fixtures for hardcoded credentials. The app uses `/api/v1/token/` endpoint for token-based auth.
- **Credentials found in code**: NO hardcoded credentials found. Credentials must be provided by a running backend or mocked API.
