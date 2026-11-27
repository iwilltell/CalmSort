from pathlib import Path
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.duplicate_finder import DuplicateFinder
from core.watcher import FolderWatcher
from ui.preview_frame import PreviewFrame


class AppWindow(ctk.CTk):
    def __init__(self, engine, history_manager):
        super().__init__()
        self.engine = engine
        self.history_manager = history_manager
        self.duplicate_finder = DuplicateFinder()
        self.watcher = FolderWatcher(engine=self.engine, on_sorted_callback=self._on_live_watch_sorted)

        self.title("CalmSort — Automated Desktop File Management")
        self.geometry("1120x680")
        self.minsize(960, 600)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        default_downloads = Path.home() / "Downloads"
        self.selected_folder = str(default_downloads if default_downloads.exists() else Path.home())
        self.current_plan = []
        self.dup_checkboxes = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_container()
        self.show_view("organize")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        badge = ctk.CTkLabel(
            self.sidebar,
            text="CS",
            width=54,
            height=54,
            corner_radius=27,
            fg_color="#3B82F6",
            text_color="white",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        badge.grid(row=0, column=0, padx=20, pady=(24, 6))

        brand = ctk.CTkLabel(self.sidebar, text="CalmSort", font=ctk.CTkFont(size=20, weight="bold"))
        brand.grid(row=1, column=0, padx=20, pady=(0, 24))

        self.nav_buttons = {}
        nav_items = [
            ("organize", "Organize"),
            ("rules", "Rules"),
            ("duplicates", "Duplicates"),
            ("history", "History")
        ]
        for idx, (key, label) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                height=38,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25"),
                command=lambda k=key: self.show_view(k)
            )
            btn.grid(row=idx, column=0, padx=16, pady=6, sticky="ew")
            self.nav_buttons[key] = btn

        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Dark Mode",
            command=self._toggle_theme
        )
        self.theme_switch.select()
        self.theme_switch.grid(row=7, column=0, padx=20, pady=(10, 24), sticky="w")

    def _build_main_container(self):
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        self.views = {
            "organize": self._create_organize_view(),
            "rules": self._create_rules_view(),
            "duplicates": self._create_duplicates_view(),
            "history": self._create_history_view()
        }

    def show_view(self, key: str):
        for name, frame in self.views.items():
            if name == key:
                frame.grid(row=0, column=0, sticky="nsew")
                self.nav_buttons[name].configure(fg_color=("#CBD5E1", "#1E3A5F"))
            else:
                frame.grid_forget()
                self.nav_buttons[name].configure(fg_color="transparent")

        if key == "rules":
            self._refresh_rules_list()
        elif key == "history":
            self._refresh_history_list()
        elif key == "organize":
            self._update_metrics()

    # ---------------- ORGANIZE VIEW ----------------
    def _create_organize_view(self):
        frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        header = ctk.CTkLabel(
            frame,
            text="Automated File Management Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # Folder Picker + Live Watch Bar
        bar = ctk.CTkFrame(frame)
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        bar.grid_columnconfigure(0, weight=1)

        self.folder_label = ctk.CTkLabel(bar, text=f"Target: {self.selected_folder}", anchor="w")
        self.folder_label.grid(row=0, column=0, padx=14, pady=12, sticky="ew")

        self.watch_switch = ctk.CTkSwitch(bar, text="Live Watch", command=self.toggle_watchdog)
        self.watch_switch.grid(row=0, column=1, padx=10, pady=12)

        pick_btn = ctk.CTkButton(bar, text="Select Target Folder", command=self.select_directory)
        pick_btn.grid(row=0, column=2, padx=8, pady=12)

        preview_btn = ctk.CTkButton(bar, text="Scan & Preview", fg_color="#2563EB", command=self.scan_and_preview)
        preview_btn.grid(row=0, column=3, padx=(4, 14), pady=12)

        # Metric Cards
        cards = ctk.CTkFrame(frame, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_scanned = self._make_metric_card(cards, 0, "Files Ready in Folder", "0")
        self.card_sorted = self._make_metric_card(cards, 1, "Total Files Sorted", "0")
        self.card_sessions = self._make_metric_card(cards, 2, "Logged Sessions", "0")

        # Dry-Run Preview Table
        self.preview_table = PreviewFrame(frame, label_text="Dry-Run Preview (Uncheck files to skip)")
        self.preview_table.grid(row=3, column=0, sticky="nsew", pady=(0, 12))

        # Bottom Action & Progress Bar
        footer = ctk.CTkFrame(frame)
        footer.grid(row=4, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(footer)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, padx=14, pady=14, sticky="ew")

        self.status_lbl = ctk.CTkLabel(footer, text="Ready", width=180, anchor="e")
        self.status_lbl.grid(row=0, column=1, padx=10, pady=14)

        self.sort_btn = ctk.CTkButton(
            footer,
            text="Confirm Checked Moves",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.start_sorting_thread
        )
        self.sort_btn.grid(row=0, column=2, padx=(6, 14), pady=14)

        return frame

    def _make_metric_card(self, parent, col, title, initial_val):
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=col, padx=6, sticky="ew")
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(12, 2))
        val_lbl = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(size=24, weight="bold"))
        val_lbl.pack(pady=(0, 12))
        return val_lbl

    def _update_metrics(self):
        try:
            files = self.engine.scan_directory(self.selected_folder)
            self.card_scanned.configure(text=str(len(files)))
        except ValueError:
            self.card_scanned.configure(text="0")

        history = self.history_manager.load_history()
        total_sorted = sum(s.get("files_moved", 0) for s in history if not s.get("undone", False))
        self.card_sorted.configure(text=str(total_sorted))
        self.card_sessions.configure(text=str(len(history)))

    def select_directory(self):
        chosen = filedialog.askdirectory(initialdir=self.selected_folder)
        if chosen:
            self.selected_folder = chosen
            self.folder_label.configure(text=f"Target: {self.selected_folder}")
            self._update_metrics()
            self.scan_and_preview()

    def scan_and_preview(self):
        try:
            self.current_plan = self.engine.generate_plan(self.selected_folder)
            self.preview_table.populate(self.current_plan)
            self.card_scanned.configure(text=str(len(self.current_plan)))
            self.status_lbl.configure(text=f"{len(self.current_plan)} file(s) previewed")
            self.progress_bar.set(0)
        except ValueError as err:
            messagebox.showerror("Invalid Folder", str(err))

    def start_sorting_thread(self):
        approved = self.preview_table.get_approved_moves()
        if not approved:
            messagebox.showinfo("Nothing Selected", "Scan a folder and select at least one file to sort.")
            return

        self.sort_btn.configure(state="disabled")
        self.progress_bar.set(0)

        def worker():
            def on_progress(curr, total, filename):
                self.after(0, lambda: self.progress_bar.set(curr / total))
                self.after(0, lambda: self.status_lbl.configure(text=f"Moving {curr}/{total}..."))

            result = self.engine.execute_plan(self.selected_folder, approved, progress_callback=on_progress)
            self.after(0, lambda: self._on_sort_finished(result))

        threading.Thread(target=worker, daemon=True).start()

    def _on_sort_finished(self, result: dict):
        self.sort_btn.configure(state="normal")
        moved = result.get("moved_count", 0)
        session = result.get("session")
        self.status_lbl.configure(text=f"Sorted {moved} file(s)")
        self._update_metrics()
        self.scan_and_preview()
        if session:
            messagebox.showinfo(
                "Sort Complete",
                f"Successfully moved {moved} file(s) in Session #{session['session_id']}.\n"
                "You can revert this session anytime from the History tab."
            )

    def toggle_watchdog(self):
        if self.watch_switch.get() == 1:
            try:
                self.watcher.start(self.selected_folder)
                self.status_lbl.configure(text="Live Watch ON")
            except ValueError as err:
                self.watch_switch.deselect()
                messagebox.showerror("Live Watch Error", str(err))
        else:
            self.watcher.stop()
            self.status_lbl.configure(text="Live Watch OFF")

    def _on_live_watch_sorted(self, filename: str, category: str):
        self.after(0, lambda: self.status_lbl.configure(text=f"Auto-sorted {filename} -> {category}"))
        self.after(0, self._update_metrics)

    # ---------------- RULES VIEW ----------------
    def _create_rules_view(self):
        frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            frame,
            text="Custom Sorting Rules Manager",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        form = ctk.CTkFrame(frame)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        form.grid_columnconfigure((0, 1, 2), weight=1)

        self.rule_cat_entry = ctk.CTkEntry(form, placeholder_text="Category (e.g. Finance)")
        self.rule_cat_entry.grid(row=0, column=0, padx=10, pady=12, sticky="ew")

        self.rule_ext_entry = ctk.CTkEntry(form, placeholder_text="Extensions (e.g. .pdf, .xlsx)")
        self.rule_ext_entry.grid(row=0, column=1, padx=10, pady=12, sticky="ew")

        self.rule_kw_entry = ctk.CTkEntry(form, placeholder_text="Keywords (e.g. invoice, receipt)")
        self.rule_kw_entry.grid(row=0, column=2, padx=10, pady=12, sticky="ew")

        add_btn = ctk.CTkButton(form, text="Save Rule", command=self._save_rule)
        add_btn.grid(row=0, column=3, padx=(6, 12), pady=12)

        self.rules_scroll = ctk.CTkScrollableFrame(frame, label_text="Active Rules (Keywords take priority over extensions)")
        self.rules_scroll.grid(row=2, column=0, sticky="nsew")
        self.rules_scroll.grid_columnconfigure(0, weight=1)
        return frame

    def _refresh_rules_list(self):
        for w in self.rules_scroll.winfo_children():
            w.destroy()

        rules = self.history_manager.load_rules()
        for idx, (cat, data) in enumerate(rules.items()):
            row = ctk.CTkFrame(self.rules_scroll)
            row.grid(row=idx, column=0, padx=8, pady=5, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(size=14, weight="bold"), width=130, anchor="w").grid(
                row=0, column=0, padx=12, pady=10
            )
            exts = ", ".join(data.get("extensions", [])) or "None"
            kws = ", ".join(data.get("keywords", [])) or "None"
            ctk.CTkLabel(row, text=f"Extensions: {exts}   |   Keywords: {kws}", anchor="w").grid(
                row=0, column=1, padx=8, pady=10, sticky="ew"
            )
            ctk.CTkButton(
                row,
                text="Delete",
                width=70,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda c=cat: self._delete_rule(c)
            ).grid(row=0, column=2, padx=12, pady=10)

    def _save_rule(self):
        cat = self.rule_cat_entry.get().strip()
        if not cat:
            messagebox.showwarning("Missing Category", "Please enter a category folder name.")
            return
        exts = [x.strip() for x in self.rule_ext_entry.get().split(",") if x.strip()]
        kws = [x.strip() for x in self.rule_kw_entry.get().split(",") if x.strip()]
        self.history_manager.add_or_update_rule(cat, exts, kws)
        self.rule_cat_entry.delete(0, "end")
        self.rule_ext_entry.delete(0, "end")
        self.rule_kw_entry.delete(0, "end")
        self._refresh_rules_list()

    def _delete_rule(self, category: str):
        self.history_manager.delete_rule(category)
        self._refresh_rules_list()

    # ---------------- DUPLICATES VIEW ----------------
    def _create_duplicates_view(self):
        frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            frame,
            text="SHA-256 Duplicate File Finder",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        top = ctk.CTkFrame(frame)
        top.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        top.grid_columnconfigure(0, weight=1)

        self.dup_summary_lbl = ctk.CTkLabel(top, text="Click 'Scan for Duplicates' to analyze the target folder.", anchor="w")
        self.dup_summary_lbl.grid(row=0, column=0, padx=14, pady=12, sticky="ew")

        ctk.CTkButton(top, text="Scan for Duplicates", command=self._scan_duplicates).grid(
            row=0, column=1, padx=8, pady=12
        )
        ctk.CTkButton(
            top,
            text="Delete Checked Duplicates",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self._delete_selected_duplicates
        ).grid(row=0, column=2, padx=(4, 14), pady=12)

        self.dup_scroll = ctk.CTkScrollableFrame(frame, label_text="Duplicate File Groups (Original copy is unchecked by default)")
        self.dup_scroll.grid(row=2, column=0, sticky="nsew")
        self.dup_scroll.grid_columnconfigure(0, weight=1)
        return frame

    def _scan_duplicates(self):
        for w in self.dup_scroll.winfo_children():
            w.destroy()
        self.dup_checkboxes.clear()

        try:
            res = self.duplicate_finder.find_duplicates(self.selected_folder, recursive=True)
        except ValueError as err:
            messagebox.showerror("Scan Error", str(err))
            return

        size_str = self.duplicate_finder.format_size(res["recoverable_bytes"])
        self.dup_summary_lbl.configure(
            text=f"Found {res['group_count']} duplicate group(s) — Recoverable space: {size_str}"
        )

        if not res["groups"]:
            ctk.CTkLabel(self.dup_scroll, text="No duplicate files detected.", text_color="gray").grid(
                row=0, column=0, pady=24
            )
            return

        for g_idx, group in enumerate(res["groups"]):
            card = ctk.CTkFrame(self.dup_scroll)
            card.grid(row=g_idx, column=0, padx=8, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            f_size = self.duplicate_finder.format_size(group["size_bytes"])
            ctk.CTkLabel(
                card,
                text=f"Group #{g_idx + 1}  |  SHA-256: {group['hash']}...  |  Size: {f_size} each",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).grid(row=0, column=0, padx=12, pady=(8, 4), sticky="ew")

            for f_idx, fp in enumerate(group["files"]):
                var = ctk.BooleanVar(value=(f_idx > 0))  # Keep first copy unchecked
                self.dup_checkboxes.append((var, fp))
                tag = "[KEEP ORIGINAL] " if f_idx == 0 else "[DUPLICATE] "
                ctk.CTkCheckBox(card, text=f"{tag}{fp}", variable=var).grid(
                    row=f_idx + 1, column=0, padx=18, pady=3, sticky="w"
                )

    def _delete_selected_duplicates(self):
        to_delete = [fp for var, fp in self.dup_checkboxes if var.get()]
        if not to_delete:
            messagebox.showinfo("No Selection", "Select at least one duplicate file to delete.")
            return
        if messagebox.askyesno("Confirm Deletion", f"Permanently delete {len(to_delete)} selected duplicate file(s)?"):
            deleted = self.duplicate_finder.delete_files(to_delete)
            messagebox.showinfo("Cleanup Complete", f"Deleted {deleted} duplicate file(s).")
            self._scan_duplicates()

    # ---------------- HISTORY & UNDO VIEW ----------------
    def _create_history_view(self):
        frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            frame,
            text="Activity Log & Reversible Sessions",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        bar = ctk.CTkFrame(frame)
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(bar, text="Revert any completed sorting session back to original locations.", anchor="w").grid(
            row=0, column=0, padx=14, pady=12, sticky="ew"
        )
        ctk.CTkButton(
            bar,
            text="Undo Latest Session",
            fg_color="#D97706",
            hover_color="#B45309",
            command=self.undo_last_session
        ).grid(row=0, column=1, padx=14, pady=12)

        self.history_scroll = ctk.CTkScrollableFrame(frame, label_text="Session History")
        self.history_scroll.grid(row=2, column=0, sticky="nsew")
        self.history_scroll.grid_columnconfigure(0, weight=1)
        return frame

    def _refresh_history_list(self):
        for w in self.history_scroll.winfo_children():
            w.destroy()

        history = list(reversed(self.history_manager.load_history()))
        if not history:
            ctk.CTkLabel(self.history_scroll, text="No sorting sessions recorded yet.", text_color="gray").grid(
                row=0, column=0, pady=24
            )
            return

        for idx, session in enumerate(history):
            card = ctk.CTkFrame(self.history_scroll)
            card.grid(row=idx, column=0, padx=8, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            status_txt = "UNDONE" if session.get("undone") else "ACTIVE"
            header = (
                f"Session #{session['session_id']}  |  {session['timestamp']}  |  "
                f"Mode: {session.get('source', 'Manual Sort')}  |  Files: {session['files_moved']}  |  [{status_txt}]"
            )
            ctk.CTkLabel(card, text=header, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(
                row=0, column=0, padx=12, pady=(8, 2), sticky="ew"
            )
            ctk.CTkLabel(card, text=f"Target: {session['target_dir']}", text_color="gray", anchor="w").grid(
                row=1, column=0, padx=12, pady=(0, 8), sticky="ew"
            )

            if not session.get("undone"):
                ctk.CTkButton(
                    card,
                    text="Undo This Session",
                    width=130,
                    command=lambda sid=session["session_id"]: self._undo_specific_session(sid)
                ).grid(row=0, column=1, rowspan=2, padx=12, pady=8)

    def undo_last_session(self):
        ok, msg, _ = self.history_manager.undo_session()
        if ok:
            messagebox.showinfo("Undo Complete", msg)
            self._refresh_history_list()
            self._update_metrics()
        else:
            messagebox.showwarning("Undo Unavailable", msg)

    def _undo_specific_session(self, session_id: int):
        ok, msg, _ = self.history_manager.undo_session(session_id)
        if ok:
            messagebox.showinfo("Undo Complete", msg)
            self._refresh_history_list()
            self._update_metrics()
        else:
            messagebox.showwarning("Undo Unavailable", msg)

    def _toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() == 1 else "Light")

    def _on_close(self):
        self.watcher.stop()
        self.destroy()
