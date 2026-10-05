# Grid ERP — Custom Branding & UI

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
grid_erp/
├── hooks.py                      Asset includes, branding hooks
├── assets.py                     Serves public/ files through the backend
├── branding.py                   Serves settings to desk/login; edit lock
├── modules.txt                   "Grid ERP" module
├── grid_erp/doctype/grid_branding_settings/
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

## How CSS, JS and images load

`assets.py` serves everything under `public/` from the Python backend at
`/api/method/grid_erp.assets.serve?path=<file>&v=<hash>`, not from `/assets/`.
So nothing has to be built, copied or symlinked, and nginx needs no change:
the files load on any bench or Docker setup where the app is installed.

`<hash>` is computed from the files themselves, so after editing anything in
`public/` browsers fetch the new copy automatically. No version bump is needed.

## Installing on any server

```bash
bench get-app https://github.com/akashdataanalyst/ErpNext-Demo.git
bench --site <site> install-app grid_erp   # existing site: bench --site <site> migrate
```

In Docker, the app code must be present in every Python container (backend,
queue-short, queue-long, scheduler), because they share one Redis cache.
After pulling new code, restart those containers and run
`bench --site <site> migrate`.

## Version

1.1.0 RC1
