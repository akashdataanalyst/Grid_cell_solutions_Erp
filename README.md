# Calco ERP — Custom Branding & UI

Frappe/ERPNext app for **Calco PolyTechnik Pvt Ltd**. It brands the login page,
the desk home and the workspace pages. It changes presentation only: native
routes, permissions and workspace data stay as ERPNext defines them.

## Changing logo, text or colours

Everything visible is edited from the desk, with no code change:

1. Log in as `Administrator`.
2. Open **Grid Branding Settings** (`/desk/grid-branding-settings`).
3. Click **Unlock to Edit** and enter the branding password.
4. Edit, **Save**, then refresh the page.

| Section | Controls |
| --- | --- |
| Company | Company name, ERP name, footer version, browser tab titles |
| Images | Logo, favicon, home banner image (blank = built-in Calco image) |
| Banner Text | Tagline, capabilities, values, description, footer line, workspaces heading |
| Login Page | Heading, subtitle prefix, access and connection notices |
| Colours | Primary, primary dark, dark header, text, page background |
| Workspace Order | Optional home-page order, one workspace per line |

A blank field falls back to the built-in default in `calco_workspace_config.js`.

### Access and password

- Only the `Administrator` user can open the settings (`branding.py: has_permission`).
- Editing needs the branding password; a correct password unlocks editing for
  15 minutes in that login session. Five attempts are allowed per 5 minutes.
- The code stores only a hash of the password (`branding.py: DEFAULT_PASSWORD_HASH`).
  To use a different password on one site, set `grid_branding_password_hash` in
  that site's `site_config.json` to a hash from `frappe.utils.password.passlibctx.hash()`.

## Code layout

```text
calco_erp/
├── hooks.py                      Asset includes, ASSET_VERSION, branding hooks
├── branding.py                   Serves settings to desk/login; edit lock
├── modules.txt                   "Calco ERP" module
├── calco_erp/doctype/grid_branding_settings/
│   ├── grid_branding_settings.json   Settings form fields
│   ├── grid_branding_settings.py     Save checks the lock, then clears cache
│   └── grid_branding_settings.js     Locked form + "Unlock to Edit" dialog
└── public/
    ├── js/calco_workspace_config.js  Built-in defaults, merged with the settings
    ├── js/calco_branding.js          Builds login panel, home banner, footer, brand bar
    ├── js/workspace_presentation.js  Icon + description on workspace shortcut tiles
    ├── css/calco_branding.css        1. Login  2. Brand bar  3. Desk home
    ├── css/workspace_presentation.css  Workspace page cards
    └── images/                       Default logo, favicon, banner
```

How the settings reach the page: `branding.py` adds them to `frappe.boot` on
the desk and to an inline `<script>` in `<head>` on website/login pages.
`calco_workspace_config.js` merges them over its defaults into
`window.calcoWorkspaceViewConfig`, which `calco_branding.js` reads.

## Changing CSS or JS

After editing any file under `public/`, bump `ASSET_VERSION` in `hooks.py`,
otherwise browsers keep serving the cached copy.

## Deployment (frappe_docker)

The app is baked into the `custom/erpnext-hrms-calco` image
(`frappe_docker/Dockerfile.custom`). After changing code:

1. Rebuild the image and recreate **all** containers (backend, frontend,
   queue-short, queue-long, scheduler, websocket). They share one Redis cache,
   so a container running older app code breaks the others.
2. Run `bench --site <site> migrate`.

On a new site, `bench --site <site> install-app calco_erp` creates the module,
the settings form and its default values.

## Version

1.1.0 RC1
