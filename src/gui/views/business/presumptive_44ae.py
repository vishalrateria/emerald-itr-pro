import customtkinter as ctk
from src.services.logging_service import log as logger
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    info_banner,
    table_header_frame,
    table_data_row,
)


class Presumptive44AESchedule:
    @staticmethod
    def create_frame(parent, fv, sl=None, validation_refs=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE 44AE — GOODS CARRIAGE",
            "Presumptive income for owners of goods carriage vehicles",
        )
        info_banner(
            f,
            "ℹ  COMPUTATION RULE",
            "Heavy vehicle (≥ 12 ton GVW): ₹1,000 × tonnage × months owned.  "
            "Light / Medium (< 12 ton): ₹7,500 per vehicle per month.",
            color=Theme.ACCENT_PRIMARY,
        )
        for i in range(10):
            tv = fv[f"ae_{i}_tonnage"]
            mv = fv[f"ae_{i}_months"]
            av = fv[f"ae_{i}_amount"]
            rv = fv[f"ae_{i}_reg"]

            def _update(_tv=tv, _mv=mv, _av=av, _rv=rv, *_args):
                if not _rv.get().strip():
                    return
                try:
                    t = float(_tv.get() or 0)
                    m = float(_mv.get() or 0)
                    calc = t * 1000 * m if t >= 12 else 7500 * m
                    if not _av.get() or _av.get() == "0":
                        _av.set(str(int(calc)))
                except (ValueError, TypeError) as e:
                    logger.debug(f"44AE calculation error: {e}")

            if hasattr(fv, "register_trace"):
                fv.register_trace(tv, "write", _update)
                fv.register_trace(mv, "write", _update)
            else:
                tv.trace_add("write", _update)
                mv.trace_add("write", _update)
        make_card(f, "VEHICLE-WISE INCOME", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("Reg No.", 1),
                ("Vehicle Type", 1),
                ("Tonnage  (tons)", 1),
                ("Months Owned", 1),
                ("Income ₹", 1),
            ],
        )
        for i in range(10):
            table_data_row(
                f,
                i,
                [
                    {
                        "textvariable": fv[f"ae_{i}_reg"],
                        "key": f"ae_{i}_reg",
                        "font": Theme.DATA,
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "values": ["Light (< 12T)", "Medium", "Heavy (≥ 12T)"],
                        "variable": fv.get(f"ae_{i}_type", ctk.StringVar()),
                        "font": Theme.BODY,
                        **Theme.get_combo_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"ae_{i}_tonnage"],
                        "key": f"ae_{i}_tonnage",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"ae_{i}_months"],
                        "key": f"ae_{i}_months",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"ae_{i}_amount"],
                        "key": f"ae_{i}_amount",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                ],
                validation_refs=validation_refs,
            )
        return f
