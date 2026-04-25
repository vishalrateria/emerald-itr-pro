import customtkinter as ctk
from ..widgets.section_label import section_label
from ..widgets.form_row import create_entry
from ..widgets.path_row import create_path_row


def build_page_pdf(dialog, p):
    section_label(p, "Practitioner Details (stamped on PDFs)")

    create_path_row(p, "Default PDF Save Folder", dialog._v_pdf_path, mode="dir")
    create_entry(p, "CA / Practitioner Name", dialog._v_ca_name, "e.g. CA Rajesh Kumar")
    create_entry(p, "CA Registration Number", dialog._v_ca_reg, "e.g. 123456W")
    create_entry(p, "Membership Number", dialog._v_membership, "e.g. 987654")
    create_entry(p, "Firm Name", dialog._v_firm_name, "e.g. Kumar & Associates")

    section_label(p, "Export Preferences")

    from src.services.settings_service import SettingsManager
    from ..widgets.form_row import create_combo, create_toggle

    create_combo(
        p,
        "Default Export Format",
        dialog._v_export_format,
        SettingsManager.get_export_format_options(),
    )
    create_combo(
        p,
        "PDF Quality Setting",
        dialog._v_pdf_quality,
        SettingsManager.get_pdf_quality_options(),
    )
    create_toggle(p, "Include Detailed Schedules in PDF", dialog._v_include_schedules)
    create_toggle(p, "Auto-open PDF After Generation", dialog._v_auto_open_pdf)
    create_combo(
        p, "JSON Export Indentation", dialog._v_json_indent, ["1", "2", "4", "Tabs"]
    )
