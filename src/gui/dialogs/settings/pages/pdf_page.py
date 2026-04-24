import customtkinter as ctk
from ..widgets.section_label import section_label
from ..widgets.form_row import create_entry
from ..widgets.path_row import create_path_row


def build_page_pdf(dialog, p):
    section_label(p, "Practitioner Details (stamped on PDFs)")

    dialog._v_pdf_path = ctk.StringVar()
    dialog._v_ca_name = ctk.StringVar()
    dialog._v_ca_reg = ctk.StringVar()
    dialog._v_firm_name = ctk.StringVar()
    dialog._v_membership = ctk.StringVar()

    create_path_row(p, "Default PDF Save Folder", dialog._v_pdf_path, mode="dir")
    create_entry(p, "CA / Practitioner Name", dialog._v_ca_name,
                "e.g. CA Rajesh Kumar")
    create_entry(p, "CA Registration Number", dialog._v_ca_reg,
                "e.g. 123456W")
    create_entry(p, "Membership Number", dialog._v_membership,
                "e.g. 987654")
    create_entry(p, "Firm Name", dialog._v_firm_name,
                "e.g. Kumar & Associates")
