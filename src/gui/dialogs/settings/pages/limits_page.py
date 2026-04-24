from ..widgets.section_label import section_label
from ..widgets.form_row import create_entry


def build_page_limits(dialog, p):
    section_label(p, "Data Entry Limits")

    dialog._v_max_bank = dialog.register_var("max_bank")
    dialog._v_max_tds = dialog.register_var("max_tds")
    dialog._v_max_tcs = dialog.register_var("max_tcs")
    dialog._v_max_vda = dialog.register_var("max_vda")
    dialog._v_max_biz = dialog.register_var("max_biz")
    dialog._v_max_hp = dialog.register_var("max_hp")
    dialog._v_max_cg = dialog.register_var("max_cg")
    dialog._v_itr1_limit = dialog.register_var("itr1_limit")

    create_entry(p, "Max Bank Accounts", dialog._v_max_bank, "5")
    create_entry(p, "Max TDS Entries", dialog._v_max_tds, "10")
    create_entry(p, "Max TCS Entries", dialog._v_max_tcs, "10")
    create_entry(p, "Max VDA Entries", dialog._v_max_vda, "10")
    create_entry(p, "Max Business Entities", dialog._v_max_biz, "10")
    create_entry(p, "Max House Properties", dialog._v_max_hp, "5")
    create_entry(p, "Max Capital Gains Entries", dialog._v_max_cg, "10")

    section_label(p, "Compliance Limits")
    create_entry(p, "ITR-1 GTI Limit (₹)", dialog._v_itr1_limit, "5000000")
