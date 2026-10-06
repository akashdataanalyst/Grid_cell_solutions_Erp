from . import __version__ as app_version

app_name = "grid_erp"
app_title = "Grid ERP"
app_publisher = "Calco PolyTechnik Pvt Ltd"
app_description = "Calco PolyTechnik Manufacturing ERP - Branding, WhatsApp and Recruitment Assessment"
app_email = "mis.1@calco.in"
app_license = "Proprietary"
app_version = app_version
# Recruitment Assessment builds on Job Opening / Job Applicant from HRMS.
required_apps = ["frappe", "erpnext", "hrms"]

# This app has three modules (see modules.txt):
#   Grid ERP               grid_erp/grid_erp                branding, desktop
#   Grid WhatsApp          grid_erp/grid_whatsapp           WhatsApp messaging
#   Recruitment Assessment grid_erp/recruitment_assessment  online candidate assessments

# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

# Served by grid_erp.assets (Python backend), not /assets, so they load on any
# setup without building assets. URLs change automatically when a file changes.
from grid_erp.assets import url as _asset

# Desk (logged-in) pages. calco_workspace_config.js must load before calco_branding.js.
app_include_css = [
	_asset("css/calco_branding.css"),
	_asset("css/workspace_presentation.css"),
]
app_include_js = [
	_asset("js/calco_workspace_config.js"),
	_asset("js/calco_branding.js"),
	_asset("js/workspace_presentation.js"),
]

# Website pages, including the login page.
web_include_css = [_asset("css/calco_branding.css")]
web_include_js = [
	_asset("js/calco_workspace_config.js"),
	_asset("js/calco_branding.js"),
]

# ---------------------------------------------------------------------------
# Grid Branding Settings (see branding.py)
# ---------------------------------------------------------------------------

# Desk receives the settings through boot, website/login pages through <head>.
boot_session = [
	"grid_erp.branding.boot_session",
	# Lets Business Suite > folder > icon nest three levels deep (see desktop.py).
	"grid_erp.desktop.add_nested_desktop_icons",
]
update_website_context = "grid_erp.branding.update_website_context"

# Only the Administrator user may open the settings.
has_permission = {
	"Grid Branding Settings": "grid_erp.branding.has_permission",
}

# ---------------------------------------------------------------------------
# Grid WhatsApp (module grid_erp/grid_whatsapp, merged from the former
# grid_whatsapp app). See grid_whatsapp/README.md and docs/whatsapp.md.
# ---------------------------------------------------------------------------

# Desktop: "Business Suite" folder grouping WhatsApp, Recruitment and Grid.
# Install also creates the starter WhatsApp setup (instance, settings, templates, rules).
after_install = [
	"grid_erp.desktop.sync_business_suite",
	"grid_erp.grid_whatsapp.seed.seed_all",
	"grid_erp.recruitment_assessment.install.after_install",
]
after_migrate = [
	"grid_erp.desktop.sync_business_suite",
	"grid_erp.recruitment_assessment.install.after_migrate",
]
before_uninstall = "grid_erp.recruitment_assessment.install.before_uninstall"

before_install = "grid_erp.grid_whatsapp.install.ensure_manager_role"
before_migrate = "grid_erp.grid_whatsapp.install.ensure_manager_role"

# Every document event goes to the notification engine. It returns after one
# cached lookup when the DocType has no enabled WhatsApp Notification Rule.
_whatsapp_handler = "grid_erp.grid_whatsapp.services.notification_engine.handle_doc_event"
_assessment_sync = "grid_erp.recruitment_assessment.workflow.sync_job_applicant_assessment"
doc_events = {
	"*": {
		"after_insert": _whatsapp_handler,
		"on_update": _whatsapp_handler,
		"on_submit": _whatsapp_handler,
		"on_cancel": _whatsapp_handler,
		"on_change": _whatsapp_handler,
	},
	# Recruitment Assessment: keep the applicant's assessment fields in sync and
	# auto-send the assessment on Shortlist.
	"Job Applicant": {
		"after_insert": _assessment_sync,
		"on_update": _assessment_sync,
	},
}

scheduler_events = {
	"cron": {
		# Re-queue WhatsApp messages whose retry time has come.
		"* * * * *": ["grid_erp.grid_whatsapp.services.dispatcher.process_due_retries"],
	},
	# Recruitment Assessment
	"all": [
		"grid_erp.recruitment_assessment.scheduler.process_due_notifications",
	],
	"hourly": [
		"grid_erp.recruitment_assessment.scheduler.send_assessment_reminders",
		"grid_erp.recruitment_assessment.scheduler.expire_pending_assignments",
	],
	"daily": [
		"grid_erp.recruitment_assessment.scheduler.recompute_results",
	],
}

# WhatsApp providers: name -> class implementing
# grid_erp.grid_whatsapp.services.whatsapp_provider.WhatsAppProvider.
whatsapp_providers = {
	"eValidation": "grid_erp.grid_whatsapp.services.providers.evalidation.EValidationProvider",
	"Evolution API": "grid_erp.grid_whatsapp.services.providers.evolution.EvolutionProvider",
}

default_log_clearing_doctypes = {
	"WhatsApp Notification Log": 180,
}


# ---------------------------------------------------------------------------
# Recruitment Assessment (module grid_erp/recruitment_assessment, merged from
# the former akash_recruitment_assessment app). See docs/recruitment.md.
# Install / migrate / uninstall and the Job Applicant event are registered above.
# ---------------------------------------------------------------------------

# Desk form scripts. Files live in public/js/recruitment_assessment/.
doctype_js = {
	"Job Applicant": "public/js/recruitment_assessment/job_applicant.js",
	"Job Opening": "public/js/recruitment_assessment/job_opening.js",
	"Assessment Assignment": "public/js/recruitment_assessment/assessment_assignment.js",
	"Assessment Attempt": "public/js/recruitment_assessment/assessment_attempt.js",
	"Assessment Template": "public/js/recruitment_assessment/assessment_template.js",
}
doctype_list_js = {
	"Job Applicant": "public/js/recruitment_assessment/job_applicant_list.js",
	"Assessment Assignment": "public/js/recruitment_assessment/assessment_assignment_list.js",
}

# Candidate portal: www/assessment-portal (loads public/js/recruitment_assessment/proctoring.js).
website_route_rules = [
	{"from_route": "/assessment-portal/<path:app_path>", "to_route": "assessment-portal"},
]
website_context = {
	"favicon": "/assets/frappe/images/favicon.png",
}

# Job Applicant > Interview / Assessment summary also lists open assessments.
override_whitelisted_methods = {
	"hrms.hr.doctype.job_applicant.job_applicant.get_interview_details": "grid_erp.recruitment_assessment.integration.get_interview_details",
}

fixtures = [
	{
		"doctype": "Email Template",
		"filters": [["name", "=", "Assessment Invitation"]],
	},
]
