# Grid ERP

Frappe/ERPNext app for **Calco PolyTechnik Pvt Ltd**. One app, three modules:

| Module | Folder | What it does | Docs |
| --- | --- | --- | --- |
| Grid ERP | `grid_erp/grid_erp/` | Branding of login, desk home and workspaces; Business Suite desktop folder | this README |
| Grid WhatsApp | `grid_erp/grid_whatsapp/` | WhatsApp messages and notification rules | `grid_erp/grid_whatsapp/README.md`, `docs/whatsapp.md` |
| Recruitment Assessment | `grid_erp/recruitment_assessment/` | Online candidate assessments for HRMS Job Applicants | `docs/recruitment.md`, `docs/recruitment-internals.md` |

Needs `erpnext` and `hrms`. Grid WhatsApp and Recruitment Assessment were separate apps
(`grid_whatsapp`, `akash_recruitment_assessment`) and are now modules of this app. The merge
moved files and renamed import paths only; the logic is unchanged.

At a glance:

```text
grid_erp/
├── README.md                     module table + full file tree (below)
├── docs/                         whatsapp.md, recruitment.md, recruitment-internals.md
└── grid_erp/
    ├── hooks.py                  one section per module
    ├── grid_erp/                 Branding module
    ├── grid_whatsapp/            WhatsApp module
    ├── recruitment_assessment/   Assessment module (doctypes, reports, workflow, api…)
    ├── www/assessment-portal/    Candidate portal
    ├── workspace_sidebar/        4 sidebars
    └── public/js/recruitment_assessment/, public/css/recruitment_assessment/
```

On the desk all three modules sit in one folder: **Business Suite** → Communication (WhatsApp),
Hiring (Recruitment Assessment, Assessment Result), Grid.

## Branding

The branding changes presentation only: native routes, permissions and workspace
data stay as ERPNext defines them.

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
grid_erp/                                  repository root
├── README.md                              this file
├── pyproject.toml
├── docs/
│   ├── whatsapp.md                        Grid WhatsApp guide
│   ├── recruitment.md                     Recruitment process, step by step (Hinglish)
│   └── recruitment-internals.md           Recruitment internals: documents, fields, flow
└── grid_erp/                              the Python package (the app)
    ├── hooks.py                           All hooks, one section per module
    ├── modules.txt                        Grid ERP, Grid WhatsApp, Recruitment Assessment
    ├── patches.txt / patches/             Data patches (patches/recruitment_assessment/)
    ├── fixtures/                          "Assessment Invitation" Email Template
    │
    │   ── shared app files ──
    ├── assets.py                          Serves public/ files through the backend
    ├── branding.py                        Serves branding settings to desk/login; edit lock
    ├── desktop.py                         Business Suite desktop folder (all modules)
    ├── workspace_sidebar/                 Sidebars: grid, whatsapp, recruitment_assessment, assessment_result
    │
    │   ── modules ──
    ├── grid_erp/                          Module "Grid ERP"
    │   └── doctype/grid_branding_settings/
    ├── grid_whatsapp/                     Module "Grid WhatsApp"
    │   ├── doctype/                       WhatsApp Instance, Settings, Template, Notification Rule/Log …
    │   ├── services/                      notification engine, dispatcher, providers (Evolution, eValidation)
    │   ├── api/                           webhook, notification APIs
    │   └── install.py, seed.py, seed_data/, tests/, utils/
    ├── recruitment_assessment/            Module "Recruitment Assessment"
    │   ├── doctype/                       Assessment Template/Assignment/Attempt/Result, Question Bank, Settings …
    │   ├── report/                        Leaderboard, pending/completed/expired, violations, analytics
    │   ├── workspace/                     "Recruitment Assessment" workspace page
    │   ├── workflow.py                    Template choice + auto-send on Shortlist
    │   ├── service.py                     Assignment, login, start, autosave, submit, scoring
    │   ├── api.py                         Whitelisted APIs for the portal and HR
    │   ├── notifications.py               Invitation email
    │   ├── install.py, seed.py            Custom fields, roles, starter templates
    │   └── scheduler.py, evaluation.py, ai_evaluation.py, certificate.py, …
    │
    ├── www/assessment-portal/             Candidate portal page (/assessment-portal)
    └── public/
        ├── js/
        │   ├── calco_workspace_config.js  Branding: built-in defaults, merged with the settings
        │   ├── calco_branding.js          Branding: login panel, home banner, footer, brand bar
        │   ├── workspace_presentation.js  Branding: icon + description on workspace tiles
        │   └── recruitment_assessment/    Desk form scripts (job_applicant.js, assessment_*.js …)
        │                                  + proctoring.js (candidate portal)
        ├── css/
        │   ├── calco_branding.css, workspace_presentation.css
        │   └── recruitment_assessment/proctoring.css
        ├── icons/desktop_icons/{solid,subtle}/   Business Suite icons
        └── images/                        Default logo, favicon, banner
```

How the settings reach the page: `branding.py` adds them to `frappe.boot` on
the desk and to an inline `<script>` in `<head>` on website/login pages.
`calco_workspace_config.js` merges them over its defaults into
`window.calcoWorkspaceViewConfig`, which `calco_branding.js` reads.

## How CSS, JS and images load

Branding files: `assets.py` serves everything under `public/` from the Python backend at
`/api/method/grid_erp.assets.serve?path=<file>&v=<hash>`, not from `/assets/`.
So nothing has to be built, copied or symlinked, and nginx needs no change:
the files load on any bench or Docker setup where the app is installed.

`<hash>` is computed from the files themselves, so after editing anything in
`public/` browsers fetch the new copy automatically. No version bump is needed.

Recruitment Assessment files load the normal Frappe way: desk form scripts through
`doctype_js` in `hooks.py`, and the portal page from `/assets/grid_erp/...`. After
changing `proctoring.js` or `proctoring.css`, bump `?v=` in
`www/assessment-portal/index.html`.

## Recruitment Assessment flow

```text
Job Applicant marked Shortlisted
  → hooks.py doc_events → recruitment_assessment/workflow.py (template: Job Opening, else default)
  → service.create_assignment → notifications.py emails the link immediately
  → candidate takes the test at /assessment-portal (proctoring.js, api.py)
  → Assessment Attempt (answers + one camera video with audio) → Assessment Result
  → HR scores on the Attempt form → Job Applicant "Assessment" tab updates
```

- Auto-send on Shortlist: **Assessment Settings > Auto-send Assessment on Shortlist**
  (on by default), or per Job Opening with *Auto-assign on Shortlist*.
- Manual: Job Applicant > Assessment > **Assign Assessment** (or **Assign Another Assessment**)
  to send any template.
- Step-by-step process: `docs/recruitment.md`. Documents, fields, code map:
  `docs/recruitment-internals.md`.

## Installing on any server

```bash
bench get-app https://github.com/akashdataanalyst/ErpNext-Demo.git
bench --site <site> install-app grid_erp   # existing site: bench --site <site> migrate
```

In Docker, the app code must be present in every Python container (backend,
queue-short, queue-long, scheduler), because they share one Redis cache.
After pulling new code, restart those containers and run
`bench --site <site> migrate`.

This setup (`~/frappe_docker/pwd.yml`) bind-mounts `custom_apps/hrms` and
`custom_apps/grid_erp` into every container, so code changes need no `docker cp`:

```bash
cd ~/frappe_docker
docker-compose -p frappe_docker -f pwd.yml restart backend queue-short queue-long scheduler
docker exec frappe_docker_backend_1 bench --site ampugerp.in migrate
docker exec frappe_docker_backend_1 bench --site ampugerp.in clear-cache
```

After editing `public/js/recruitment_assessment/proctoring.js` or its CSS, bump `?v=` in
`www/assessment-portal/index.html`.

## Version

1.1.0 RC1
