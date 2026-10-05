from . import __version__ as app_version

app_name = "grid_erp"
app_title = "Grid ERP"
app_publisher = "Calco PolyTechnik Pvt Ltd"
app_description = "Calco PolyTechnik Manufacturing ERP - Custom Branding & UI"
app_email = "mis.1@calco.in"
app_license = "Proprietary"
app_version = app_version

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
boot_session = "grid_erp.branding.boot_session"
update_website_context = "grid_erp.branding.update_website_context"

# Only the Administrator user may open the settings.
has_permission = {
	"Grid Branding Settings": "grid_erp.branding.has_permission",
}

# ---------------------------------------------------------------------------
# Grid WhatsApp (module grid_erp/grid_whatsapp, merged from the former
# grid_whatsapp app). See grid_whatsapp/README.md and whatsapp.md.
# ---------------------------------------------------------------------------

before_install = "grid_erp.grid_whatsapp.install.ensure_manager_role"
before_migrate = "grid_erp.grid_whatsapp.install.ensure_manager_role"

# Every document event goes to the notification engine. It returns after one
# cached lookup when the DocType has no enabled WhatsApp Notification Rule.
_whatsapp_handler = "grid_erp.grid_whatsapp.services.notification_engine.handle_doc_event"
doc_events = {
	"*": {
		"after_insert": _whatsapp_handler,
		"on_update": _whatsapp_handler,
		"on_submit": _whatsapp_handler,
		"on_cancel": _whatsapp_handler,
		"on_change": _whatsapp_handler,
	}
}

scheduler_events = {
	"cron": {
		# Re-queue WhatsApp messages whose retry time has come.
		"* * * * *": ["grid_erp.grid_whatsapp.services.dispatcher.process_due_retries"],
	},
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
