"""Business Suite: one desktop folder that groups the custom apps.

    Business Suite
    ├── Communication  → WhatsApp (its sidebar also holds the notification rules)
    ├── Hiring         → Recruitment Assessment, Assessment Result
    └── Grid

Desktop Icon names are their labels and must be unique, so the folder cannot reuse
"Recruitment" (HRMS).

Two pieces:
1. `sync_business_suite` (after_migrate) creates / re-parents the icons. Link icons point at
   Workspace Sidebars of the same name (grid_erp/workspace_sidebar). Icon artwork:
   grid_erp/public/icons/desktop_icons/{solid,subtle}.
2. `add_nested_desktop_icons` (boot_session). Frappe's get_desktop_icons only keeps icons whose
   parent is a top-level icon, so Business Suite > Communication > WhatsApp would lose WhatsApp.
   This adds such deeper icons back, with the same permission rules.
"""

from __future__ import annotations

import frappe

SUITE = "Business Suite"

# label: (icon_type, parent, app, sidebar/None, idx)
SUITE_ICONS = {
	SUITE: ("Folder", None, "grid_erp", None, 0),
	"Communication": ("Folder", SUITE, "grid_erp", None, 1),
	"Hiring": ("Folder", SUITE, "grid_erp", None, 2),
	"WhatsApp": ("Link", "Communication", "grid_erp", "WhatsApp", 1),
	"Recruitment Assessment": ("Link", "Hiring", "grid_erp", "Recruitment Assessment", 1),
	"Assessment Result": ("Link", "Hiring", "grid_erp", "Assessment Result", 2),
	"Grid": ("Link", SUITE, "grid_erp", "Grid", 3),
}

# Icons / sidebars this app used to ship; removed on migrate.
OBSOLETE_ICONS = ["Operations", "Automations", "Alert Rules"]
OBSOLETE_SIDEBARS = ["Alert Rules"]

# App icon of the former akash_recruitment_assessment app (merged into grid_erp).
REMOVED_APP_ICONS = ["Akash Recruitment Assessment"]

ICON_FIELDS = [
	"label", "bg_color", "link", "link_type", "app", "icon_type", "parent_icon", "icon", "link_to",
	"idx", "standard", "logo_url", "hidden", "name", "restrict_removal", "icon_image",
]


def sync_business_suite():
	installed = set(frappe.get_installed_apps())
	for label, (icon_type, parent, app, sidebar, idx) in SUITE_ICONS.items():
		if app not in installed or (sidebar and not frappe.db.exists("Workspace Sidebar", sidebar)):
			continue
		doc = frappe.get_doc("Desktop Icon", label) if frappe.db.exists("Desktop Icon", label) else frappe.new_doc("Desktop Icon")
		doc.update(
			{
				"label": label,
				"icon_type": icon_type,
				"parent_icon": parent,
				"app": app,
				"idx": idx,
				"hidden": 0,
				"standard": 1,
				"bg_color": "blue",
				"link_type": "Workspace Sidebar" if sidebar else None,
				"link_to": sidebar,
				"link": None,
			}
		)
		doc.flags.ignore_permissions = True
		doc.save()

	for label in OBSOLETE_ICONS:
		if frappe.db.get_value("Desktop Icon", label, "app") == "grid_erp":
			frappe.delete_doc("Desktop Icon", label, ignore_permissions=True, force=True)
	for name in OBSOLETE_SIDEBARS:
		if frappe.db.get_value("Workspace Sidebar", name, "app") == "grid_erp":
			frappe.delete_doc("Workspace Sidebar", name, ignore_permissions=True, force=True)

	for label in REMOVED_APP_ICONS:
		if frappe.db.exists("Desktop Icon", label):
			frappe.delete_doc("Desktop Icon", label, ignore_permissions=True, force=True)

	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")


def add_nested_desktop_icons(bootinfo):
	icons = bootinfo.get("desktop_icons")
	if icons is None:
		return
	shown = {icon.label for icon in icons}
	sidebars = bootinfo.get("workspace_sidebar_item") or {}
	user_roles = set(frappe.get_roles())

	candidates = frappe.get_all(
		"Desktop Icon",
		filters={"hidden": 0, "parent_icon": ["is", "set"], "label": ["not in", list(shown) or [""]]},
		fields=ICON_FIELDS,
		order_by="idx asc",
	)
	if not candidates:
		return
	role_map = {}
	for row in frappe.get_all(
		"Has Role",
		filters={"parenttype": "Desktop Icon", "parent": ["in", [c.name for c in candidates]]},
		fields=["parent", "role"],
	):
		role_map.setdefault(row.parent, set()).add(row.role)

	def permitted(icon):
		if icon.icon_type == "Link":
			sidebar = sidebars.get((icon.label or "").lower())
			if not (sidebar and sidebar.get("items")):
				return False
		elif icon.icon_type == "App":
			return False  # app icons are only ever top level
		roles = role_map.get(icon.name)
		return not roles or bool(roles & user_roles)

	# Walk down level by level: a child is added once its parent is on the desktop.
	added = True
	while added:
		added = False
		for icon in candidates:
			if icon.label not in shown and icon.parent_icon in shown and permitted(icon):
				icons.append(icon)
				shown.add(icon.label)
				added = True
