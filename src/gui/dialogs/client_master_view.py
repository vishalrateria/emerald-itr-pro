from src.gui.styles.theme import Theme
import customtkinter as ctk
from tkinter import messagebox
import re
from src.gui.styles.constants import (
    ENTRY_HEIGHT,
    BUTTON_HEIGHT,
    BUTTON_HEIGHT_SM,
    CLIENT_SIDEBAR_WIDTH,
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    RADIUS_MD,
    MODAL_WIDTH_MD,
    MODAL_HEIGHT_MD,
    DIVIDER_HEIGHT,
)

class ClientMaster:
    def __init__(self, parent, on_switch_callback, on_save_switch_callback):
        self.parent = parent
        self.on_switch = on_switch_callback
        self.clients: dict = {}
        self.current_client_id = None
        self.client_list_frame = None
        self.new_client_vars = {
            "name": ctk.StringVar(value=""),
            "pan": ctk.StringVar(value=""),
            "relation": ctk.StringVar(value="Self"),
        }
        self.search_var = ctk.StringVar(value="")
        self._search_trace_token = self.search_var.trace_add(
            "write", lambda *_: self.refresh_client_list())

    def add_client(self, client_id, name, pan, relation="Self"):
        self.clients[client_id] = {
            "name": name,
            "pan": pan,
            "relation": relation,
            "last_modified": None,
            "profile_config": {
                "has_salary": False,
                "has_house_property": False,
                "has_business": False,
                "has_capital_gains": False,
                "has_stcg": False,
                "has_ltcg": False,
                "has_vda": False,
                "has_other_sources": False,
                "business_type": "presumptive",
                "itr_type": "ITR-4",
            },
        }

    def remove_client(self, client_id):
        if client_id in self.clients:
            del self.clients[client_id]

    def get_client(self, client_id):
        return self.clients.get(client_id)

    def set_current_client(self, client_id):
        if client_id in self.clients:
            self.current_client_id = client_id
            return True
        return False

    def update_client_profile_config(self, client_id, config):
        if client_id in self.clients:
            self.clients[client_id]["profile_config"] = config

    def get_all_clients(self):
        return self.clients

    @staticmethod
    def create_sidebar(
        parent, on_switch_callback, on_save_switch_callback, on_add_callback
    ):
        master = ClientMaster(parent, on_switch_callback, on_save_switch_callback)
        sidebar = ctk.CTkFrame(
            parent,
            width=CLIENT_SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=Theme.BG_PRIMARY,
        )
        hdr = ctk.CTkFrame(
            sidebar,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=RADIUS_MD,
            border_width=1,
            border_color=Theme.SECTION_BORDER,
        )
        hdr.pack(fill="x", padx=SPACING_SM, pady=(SPACING_MD, SPACING_SM))
        ctk.CTkLabel(
            hdr,
            text="CLIENT\nMASTER",
            font=Theme.H3,
            text_color=Theme.SUCCESS_GREEN,
            justify="center",
            anchor="center"
        ).pack(pady=(SPACING_MD, SPACING_XS))
        ctk.CTkLabel(
            hdr,
            text="Taxpayer Switcher",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="w",
            justify="left",
        ).pack(pady=(0, SPACING_MD))
        ctk.CTkLabel(
            sidebar,
            text="  PROFILES",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="w",
        ).pack(fill="x", padx=SPACING_SM, pady=(SPACING_XS, 0))
        sf = ctk.CTkFrame(sidebar, fg_color=Theme.BG_INPUT,
                          height=ENTRY_HEIGHT, corner_radius=RADIUS_MD)
        sf.pack(fill="x", padx=SPACING_SM, pady=(0, SPACING_SM))
        ctk.CTkEntry(
            sf,
            placeholder_text="Search clients...",
            textvariable=master.search_var,
            font=Theme.CAPTION,
            justify="left",
            fg_color="transparent",
            border_width=0,
            height=ENTRY_HEIGHT
        ).pack(fill="x", padx=SPACING_XS)
        clf = ctk.CTkScrollableFrame(sidebar, fg_color="transparent",
                                     scrollbar_button_color=Theme.SECTION_BORDER, scrollbar_button_hover_color=Theme.ACCENT_PRIMARY)
        clf.pack(fill="both", expand=True, padx=SPACING_SM, pady=(0, SPACING_XS))
        master.client_list_frame = clf
        btn_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        btn_row.pack(fill="x", padx=SPACING_SM, pady=(0, SPACING_MD))
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(
            btn_row,
            text="+ ADD",
            command=lambda: on_add_callback(master),
            height=BUTTON_HEIGHT_SM,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("primary"),
        ).grid(row=0, column=0, padx=(0, SPACING_XS), sticky="ew")
        ctk.CTkButton(
            btn_row,
            text="SAVE & SWITCH",
            command=lambda: on_save_switch_callback(master),
            height=BUTTON_HEIGHT_SM,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("secondary"),
        ).grid(row=0, column=1, padx=(SPACING_XS, 0), sticky="ew")
        sidebar.client_master = master
        return sidebar

    def refresh_client_list(self):
        if self.client_list_frame is None:
            return
        for w in self.client_list_frame.winfo_children():
            w.destroy()
        if not self.clients:
            ctk.CTkLabel(
                self.client_list_frame,
                text="No clients.\nClick + ADD.",
                font=Theme.CAPTION,
                text_color=Theme.TEXT_DIM,
                justify="center",
                anchor="center"
            ).pack(pady=SPACING_LG)
            return
        name_wrap = max(80, CLIENT_SIDEBAR_WIDTH - 36)
        query = self.search_var.get().lower()
        for cid, cd in self.clients.items():
            if query and query not in cd["name"].lower() and query not in cid.lower():
                continue
            is_active = cid == self.current_client_id
            card = ctk.CTkFrame(
                self.client_list_frame,
                fg_color=(Theme.BG_INPUT if is_active else Theme.BG_SECONDARY),
                corner_radius=RADIUS_MD,
                border_width=1,
                border_color=(Theme.ACCENT_PRIMARY if is_active else Theme.SECTION_BORDER),
            )
            card.pack(fill="x", pady=(0, SPACING_XS))
            if is_active:
                indicator = ctk.CTkFrame(
                    card, width=DIVIDER_HEIGHT, fg_color=Theme.ACCENT_PRIMARY, corner_radius=2)
                indicator.place(relx=0, rely=0.1, relheight=0.8, x=2)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(fill="x", padx=SPACING_SM, pady=(SPACING_SM, SPACING_XS))
            ctk.CTkLabel(
                info,
                text=cd["name"],
                font=Theme.BODY_BOLD,
                text_color=Theme.TEXT_PRIMARY,
                wraplength=name_wrap,
                anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                info,
                text=cd["pan"],
                font=Theme.DATA,
                text_color=Theme.TEXT_DIM,
                anchor="w",
                justify="left",
            ).pack(anchor="w", fill="x")
            ctk.CTkLabel(
                info,
                text=cd.get("relation", "Self"),
                font=Theme.CAPTION,
                text_color=Theme.TEXT_DIM,
                anchor="w",
                justify="left",
            ).pack(anchor="w", fill="x")
            af = ctk.CTkFrame(card, fg_color="transparent")
            af.pack(fill="x", padx=SPACING_SM, pady=(SPACING_XS, SPACING_SM))
            af.grid_columnconfigure(0, weight=1)
            af.grid_columnconfigure(1, weight=1)
            if not is_active:
                ctk.CTkButton(
                    af,
                    text="SWITCH",
                    height=BUTTON_HEIGHT_SM,
                    font=Theme.CAPTION,
                    command=lambda c=cid: self.on_switch(c),
                    **Theme.get_button_style("primary"),
                ).grid(row=0, column=0, padx=(0, SPACING_XS), sticky="ew")
                ctk.CTkButton(
                    af,
                    text="REMOVE",
                    height=BUTTON_HEIGHT_SM,
                    font=Theme.CAPTION,
                    command=lambda c=cid: self._handle_remove(c),
                    **Theme.get_button_style("ghost"),
                ).grid(row=0, column=1, padx=(SPACING_XS, 0), sticky="ew")
            else:
                ctk.CTkLabel(af, text="CURRENT ACTIVE PROFILE", font=Theme.CAPTION,
                             text_color=Theme.ACCENT_PRIMARY).pack(fill="x")

    def _handle_remove(self, cid):
        name = self.clients[cid]["name"]
        if messagebox.askyesno("Remove Client", f"Remove «{name}»?"):
            if self.current_client_id == cid:
                self.current_client_id = None
            self.remove_client(cid)
            self.refresh_client_list()

    def show_manager_dialog(self):
        from tkinter import filedialog, messagebox
        import json
        path = filedialog.askopenfilename(
            title="Open Client Database",
            filetypes=[("Database", "*.mcdb"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "clients" not in data:
                messagebox.showerror("Error", "Invalid or unsupported database file.")
                return
            self.clients = data["clients"]
            self.current_client_id = data.get("current_client_pan", "")
            self.refresh_client_list()
            messagebox.showinfo("Database Loaded",
                                f"Loaded {len(self.clients)} client(s) from database.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {e}")

    def cleanup(self):
        try:
            self.search_var.trace_remove("write", self._search_trace_token)
        except (ValueError, RuntimeError):
            pass

    @staticmethod
    def create_add_client_dialog(parent, master):
        d = ctk.CTkToplevel(parent)
        d.title("Add New Taxpayer")
        d.geometry(f"{MODAL_WIDTH_MD}x{MODAL_HEIGHT_MD}")
        d.configure(fg_color=Theme.BG_PRIMARY)
        d.transient(parent)
        d.grab_set()
        d.protocol("WM_DELETE_WINDOW", d.destroy)
        content = ctk.CTkFrame(d, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
        ctk.CTkLabel(
            content,
            text="ADD NEW TAXPAYER",
            font=Theme.H1,
            text_color=Theme.SUCCESS_GREEN,
            anchor="w",
            justify="left",
        ).pack(pady=SPACING_MD, anchor="w", fill="x")
        form = ctk.CTkFrame(
            content,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=RADIUS_MD,
            border_width=1,
            border_color=Theme.SECTION_BORDER,
        )
        form.pack(fill="x", pady=(0, SPACING_MD))
        for label, key in [("Full Name", "name"), ("PAN Number", "pan")]:
            ctk.CTkLabel(
                form,
                text=label,
                font=Theme.BODY,
                text_color=Theme.TEXT_DIM,
                anchor="w",
            ).pack(fill="x", padx=SPACING_MD, pady=(SPACING_MD, SPACING_XS))
            ctk.CTkEntry(
                form,
                height=ENTRY_HEIGHT,
                font=Theme.BODY,
                textvariable=master.new_client_vars[key],
                justify="left",
                **Theme.get_entry_style(),
            ).pack(fill="x", padx=SPACING_MD, pady=(0, SPACING_SM))
        ctk.CTkLabel(
            form,
            text="Relation",
            font=Theme.BODY,
            text_color=Theme.TEXT_DIM,
            anchor="w",
        ).pack(fill="x", padx=SPACING_MD, pady=(SPACING_SM, SPACING_XS))
        ctk.CTkComboBox(
            form,
            values=["Self", "Spouse", "Father", "Mother", "Child", "Other"],
            variable=master.new_client_vars["relation"],
            height=ENTRY_HEIGHT,
            font=Theme.BODY,
            **Theme.get_combo_style(),
        ).pack(fill="x", padx=SPACING_MD, pady=(0, SPACING_MD))
        def on_add():
            n = master.new_client_vars["name"].get().strip()
            p = master.new_client_vars["pan"].get().strip().upper()
            r = master.new_client_vars["relation"].get()
            pan_regex = r"^[A-Z]{3}[PCHFATBLJG][A-Z][0-9]{4}[A-Z]$"
            if not n:
                messagebox.showerror("Validation Error", "Name cannot be empty.")
                return
            if not re.match(pan_regex, p):
                messagebox.showerror(
                    "Validation Error",
                    "Enter a valid PAN (e.g. ABCDE1234F).\n4th character must be P, C, H, F, A, T, B, L, J, or G.",
                )
                return
            existing_pans = {k.upper() for k in master.clients.keys()}
            if p.upper() in existing_pans:
                messagebox.showerror(
                    "Duplicate", "A client with this PAN already exists."
                )
                return
            master.add_client(p, n, p, r)
            master.refresh_client_list()
            master.on_switch(p)
            for v in master.new_client_vars.values():
                v.set("")
            d.destroy()
        bf = ctk.CTkFrame(content, fg_color="transparent")
        bf.pack(fill="x", pady=SPACING_MD)
        bf.grid_columnconfigure(0, weight=1)
        bf.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(
            bf,
            text="ADD CLIENT",
            command=on_add,
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("primary"),
        ).grid(row=0, column=0, padx=(0, SPACING_SM), sticky="ew")
        ctk.CTkButton(
            bf,
            text="CANCEL",
            command=d.destroy,
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("secondary"),
        ).grid(row=0, column=1, padx=(SPACING_SM, 0), sticky="ew")
        Theme.apply_dark_title_bar(d)
        return d
