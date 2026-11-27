import customtkinter as ctk


class PreviewFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=2)
        self.grid_columnconfigure(4, weight=2)
        self.row_vars = []
        self.plan_items = []
        self._render_header()

    def _render_header(self):
        headers = ["[x]", "Filename", "Original Path", "Proposed Category", "Status"]
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(
                self,
                text=text,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            lbl.grid(row=0, column=col, padx=10, pady=(6, 10), sticky="ew")

    def populate(self, plan_items: list[dict]):
        for widget in self.winfo_children():
            widget.destroy()
        self.row_vars.clear()
        self.plan_items = plan_items
        self._render_header()

        if not plan_items:
            empty_lbl = ctk.CTkLabel(
                self,
                text="No sortable files found in this folder.",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            empty_lbl.grid(row=1, column=0, columnspan=5, pady=24)
            return

        for idx, item in enumerate(plan_items, start=1):
            var = ctk.BooleanVar(value=item.get("selected", True))
            self.row_vars.append(var)

            chk = ctk.CTkCheckBox(self, text="", variable=var, width=24)
            chk.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(self, text=item["filename"], anchor="w").grid(
                row=idx, column=1, padx=10, pady=5, sticky="ew"
            )
            ctk.CTkLabel(self, text=item["original_rel"], anchor="w", text_color="gray").grid(
                row=idx, column=2, padx=10, pady=5, sticky="ew"
            )
            ctk.CTkLabel(self, text=item["category"], anchor="w").grid(
                row=idx, column=3, padx=10, pady=5, sticky="ew"
            )

            status_color = "#E06C75" if "Conflict" in item["status"] else "#4ADE80"
            ctk.CTkLabel(self, text=item["status"], anchor="w", text_color=status_color).grid(
                row=idx, column=4, padx=10, pady=5, sticky="ew"
            )

    def get_approved_moves(self) -> list[dict]:
        approved = []
        for var, item in zip(self.row_vars, self.plan_items):
            if var.get():
                approved.append(item)
        return approved
