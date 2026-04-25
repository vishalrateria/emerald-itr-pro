from ..widgets.section_label import section_label
from ..widgets.form_row import create_entry


def build_page_limits(dialog, p):
    section_label(p, "Data Entry Limits")

    create_entry(p, "Max Bank Accounts", dialog._v_max_bank, "5")
    create_entry(p, "Max TDS Entries", dialog._v_max_tds, "10")
    create_entry(p, "Max TCS Entries", dialog._v_max_tcs, "10")
    create_entry(p, "Max VDA Entries", dialog._v_max_vda, "10")
    create_entry(p, "Max Business Entities", dialog._v_max_biz, "10")
    create_entry(p, "Max House Properties", dialog._v_max_hp, "5")
    create_entry(p, "Max Capital Gains Entries", dialog._v_max_cg, "10")
    create_entry(p, "Max Capital Gains Quarters", dialog._v_max_cg_quarters, "5")
    create_entry(p, "Max Foreign Asset Entries", dialog._v_max_fo, "10")
    create_entry(p, "Max Presumptive 44AD Entries", dialog._v_max_44ad, "10")
    create_entry(p, "Max Presumptive 44ADA Entries", dialog._v_max_44ada, "10")
    create_entry(p, "Max Tax Paid Entries", dialog._v_max_tax_paid, "10")
    create_entry(p, "Max Alternate Entities", dialog._v_max_ae, "10")
    create_entry(p, "Max HP Entries", dialog._v_max_entries_hp, "5")
    create_entry(p, "Max Gift Entries", dialog._v_max_g, "5")

    section_label(p, "Compliance Limits")
    create_entry(p, "ITR-1 GTI Limit (₹)", dialog._v_itr1_limit, "5,000,000")

    def format_currency(*_args):
        raw = dialog._v_itr1_limit.get().replace(",", "")
        if raw.isdigit():
            formatted = "{:,}".format(int(raw))
            if formatted != dialog._v_itr1_limit.get():
                dialog._v_itr1_limit.set(formatted)

    dialog._v_itr1_limit.trace_add("write", format_currency)
