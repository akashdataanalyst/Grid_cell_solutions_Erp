from . import __version__ as app_version

app_name = "calco_erp"
app_title = "Calco ERP"
app_publisher = "Calco PolyTechnik Pvt Ltd"
app_description = "Calco PolyTechnik Manufacturing ERP - Custom Branding & UI"
app_email = "mis.1@calco.in"
app_license = "Proprietary"
app_version = app_version

# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

# Served by calco_erp.assets (Python backend), not /assets, so they load on any
# setup without building assets. URLs change automatically when a file changes.
from calco_erp.assets import url as _asset

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
boot_session = "calco_erp.branding.boot_session"
update_website_context = "calco_erp.branding.update_website_context"

# Only the Administrator user may open the settings.
has_permission = {
	"Grid Branding Settings": "calco_erp.branding.has_permission",
}
