// The form stays read-only until the editor enters the branding password.
// The server enforces the same rule on save; this only drives the UI.
frappe.ui.form.on("Grid Branding Settings", {
	refresh(frm) {
		if (frm.doc.__onload && frm.doc.__onload.unlocked) {
			frm.dashboard.set_headline(__("Editing unlocked for 15 minutes."), "green");
			return;
		}

		frm.disable_form();
		frm.dashboard.set_headline(__("These settings are locked. Click Unlock to Edit and enter the password."), "orange");
		frm.page.set_primary_action(__("Unlock to Edit"), () => {
			const dialog = new frappe.ui.Dialog({
				title: __("Unlock Branding Settings"),
				fields: [{ fieldname: "password", fieldtype: "Password", label: __("Password"), reqd: 1 }],
				primary_action_label: __("Unlock"),
				primary_action({ password }) {
					frappe
						.call({ method: "grid_erp.branding.unlock", args: { password } })
						.then(() => {
							dialog.hide();
							// disable_form() marks every field read-only and is not reversible,
							// so start from a fresh page load.
							window.location.reload();
						});
				},
			});
			dialog.show();
		});
	},
});
