import customtkinter as ctk
import sys


def _get_dpi_scale() -> float:
    if sys.platform != "win32":
        return 1.0
    try:
        from ctypes import windll
        hdc = windll.user32.GetDC(0)
        dpi = windll.gdi32.GetDeviceCaps(hdc, 88)
        windll.user32.ReleaseDC(0, hdc)
        return max(1.0, dpi / 96.0)
    except Exception as e:
        import logging
        logging.error(f"DPI scale err: {e}")
        return 1.0


_DPI_SCALE = _get_dpi_scale()


def _fs(base: int) -> int:
    return max(base, round(base * min(_DPI_SCALE, 1.25)))


class Theme:
    BG_PRIMARY = "#121416"
    BG_SECONDARY = "#1A1D1F"
    BG_INPUT = "#232629"
    BG_RECESSED = "#0B0C0E"
    BG_HOVER = "#2D3135"

    TEXT_PRIMARY = "#F2F4F7"
    TEXT_DIM = "#94A3B8"
    TEXT_MUTED = "#64748B"

    ACCENT_PRIMARY = "#006ADC"
    ACCENT_HOVER = "#005BBF"
    BRAND_BLUE = "#006ADC"
    
    GTI_BLUE = "#339AF0"
    TTI_PURPLE = "#9775FA"
    TAX_AMBER = "#FCC419"
    SUCCESS_GREEN = "#22C55E"
    ERROR_RED = "#EF4444"
    WARNING = "#F59E0B"
    WARNING_GOLD = "#F59E0B"

    SECTION_BORDER = "#2A2E33"
    SECTION_BORDER_LIGHT = "#3F444D"

    CALC_BG = "#0A1A2F"
    CALC_BORDER = "#006ADC"
    TOTAL_BG = "#1A1608"
    TOTAL_BORDER = "#F59E0B"
    TITLE_BG = 0x00121416

    FONT_FAMILY = "Segoe UI Variable Display" if sys.platform == "win32" else "Segoe UI"
    FONT_FAMILY_DATA = "Cascadia Code" if sys.platform == "win32" else "Consolas"

    H1 = (FONT_FAMILY, _fs(18), "bold")
    H2 = (FONT_FAMILY, _fs(15), "bold")
    H3 = (FONT_FAMILY, _fs(13), "bold")
    BODY = (FONT_FAMILY, _fs(12), "normal")
    BODY_BOLD = (FONT_FAMILY, _fs(12), "bold")
    DATA = (FONT_FAMILY_DATA, _fs(12), "normal")
    DATA_BOLD = (FONT_FAMILY_DATA, _fs(12), "bold")
    CAPTION = (FONT_FAMILY, _fs(11), "normal")
    CAPTION_BOLD = (FONT_FAMILY, _fs(11), "bold")
    ICON_SM = (FONT_FAMILY, _fs(10), "normal")
    ICON_MD = (FONT_FAMILY, _fs(14), "normal")
    ICON_LG = (FONT_FAMILY, _fs(32), "normal")

    RADIUS_SM = 4
    RADIUS_MD = 6
    RADIUS_LG = 10

    @classmethod
    def set_theme_mode(cls):
        ctk.set_appearance_mode("dark")

    @classmethod
    def apply_dark_title_bar(cls, window):
        if sys.platform != "win32":
            return

        def _apply():
            try:
                from ctypes import windll, byref, sizeof, c_int
                hwnd = windll.user32.GetAncestor(window.winfo_id(), 2)
                v = c_int(1)
                windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, byref(v), sizeof(v))
                backdrop = c_int(4)
                windll.dwmapi.DwmSetWindowAttribute(hwnd, 38, byref(backdrop), sizeof(backdrop))
                c = c_int(cls.TITLE_BG)
                windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c), sizeof(c))
            except Exception as e:
                import logging
                logging.debug(f"Title bar immersion failed: {e}")
        window.after(10, _apply)

    @classmethod
    def get_entry_style(cls, variant="normal"):
        s = {
            "fg_color": cls.BG_INPUT,
            "text_color": cls.TEXT_PRIMARY,
            "border_color": cls.SECTION_BORDER,
            "border_width": 1,
            "corner_radius": cls.RADIUS_SM,
            "placeholder_text_color": cls.TEXT_MUTED
        }
        if variant == "recessed":
            s.update({"fg_color": cls.BG_RECESSED, "border_color": cls.SECTION_BORDER_LIGHT})
        elif variant == "calc":
            s.update({"fg_color": cls.CALC_BG, "border_color": cls.CALC_BORDER, "text_color": cls.BRAND_BLUE})
        elif variant == "total":
            s.update({"fg_color": cls.TOTAL_BG, "border_color": cls.TOTAL_BORDER, "text_color": cls.WARNING_GOLD})
        return s

    @classmethod
    def get_combo_style(cls):
        return {
            "fg_color": cls.BG_INPUT,
            "border_color": cls.SECTION_BORDER,
            "button_color": cls.BG_INPUT,
            "button_hover_color": cls.BG_HOVER,
            "text_color": cls.TEXT_PRIMARY,
            "dropdown_fg_color": cls.BG_SECONDARY,
            "dropdown_hover_color": cls.BG_INPUT,
            "dropdown_text_color": cls.TEXT_PRIMARY,
            "corner_radius": cls.RADIUS_SM
        }

    @classmethod
    def get_button_style(cls, variant="primary"):
        styles = {
            "primary": {
                "fg_color": cls.ACCENT_PRIMARY,
                "hover_color": cls.ACCENT_HOVER,
                "text_color": "#FFFFFF",
                "corner_radius": cls.RADIUS_SM,
            },
            "secondary": {
                "fg_color": cls.BG_INPUT,
                "border_color": cls.SECTION_BORDER_LIGHT,
                "border_width": 1,
                "hover_color": cls.BG_HOVER,
                "text_color": cls.TEXT_PRIMARY,
                "corner_radius": cls.RADIUS_SM,
            },
            "emerald": {
                "fg_color": cls.SUCCESS_GREEN,
                "hover_color": "#16A34A",
                "text_color": "#FFFFFF",
                "corner_radius": cls.RADIUS_SM,
            },
            "danger": {
                "fg_color": "transparent",
                "border_color": cls.ERROR_RED,
                "border_width": 1,
                "hover_color": "#2B1A1A",
                "text_color": cls.ERROR_RED,
                "corner_radius": cls.RADIUS_SM,
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": cls.BG_HOVER,
                "text_color": cls.TEXT_DIM,
                "corner_radius": cls.RADIUS_SM,
            },
        }
        return styles.get(variant, styles["primary"])
