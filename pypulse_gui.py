import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import PIL.Image
import PIL.ImageTk

from cleaning import GENDER_MAP, clean_fitness_data
from fitness_analytics_stats import (
    compute_all_statistics,
    build_summary_report,
    build_stakeholder_insights,
    format_display_value,
    COL_LABELS,
    NUMERIC_COLS,
    STEP_BENCHMARK,
    HIGH_INTENSITY_HR,
    LOW_SLEEP_HOURS,
    HIGH_CALORIE,
    LONG_SESSION_MIN,
)
from fitness_analytics_viz import show_all_charts
from fitness_descriptions import generate_chart_descriptions

SEARCH_PLACEHOLDER = "Search Participant / Activity..."


def _standardize_activity_label(value):
    text = str(value).strip().title().replace("Runing", "Running")
    return "HIIT" if text == "Hiit" else text


def compute_quality_metrics(raw_df):
    """Read-only UI metrics derived from the raw CSV (does not mutate data)."""
    work = raw_df.copy()
    missing_values = 0
    for col in NUMERIC_COLS:
        if col not in work.columns:
            continue
        series = work[col].replace(r"^\s*$", pd.NA, regex=True)
        missing_values += int(series.isna().sum())

    duplicate_rows = len(work) - len(work.drop_duplicates())

    inconsistent_labels = 0
    if "gender" in work.columns:
        for value in work["gender"]:
            raw = str(value).strip()
            if raw.lower() in ("nan", "none", ""):
                continue
            standardized = GENDER_MAP.get(raw, raw)
            if standardized != raw:
                inconsistent_labels += 1

    if "activity_type" in work.columns:
        for value in work["activity_type"]:
            raw = str(value).strip()
            if raw.lower() in ("nan", "none", ""):
                continue
            if _standardize_activity_label(raw) != raw:
                inconsistent_labels += 1

    return {
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "inconsistent_labels": inconsistent_labels,
    }


class PyPulseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPulse: Health & Fitness Tracking Analytics")
        self.root.geometry("1280x860")
        self.root.minsize(1000, 700)
        self.search_has_placeholder = False

        self.style = ttk.Style()
        self.configure_styles()

        self.raw_filepath = tk.StringVar(value="Group4_FitnessAnalytics_raw.csv")
        self.cleaned_filepath = tk.StringVar(value="Group4_FitnessAnalytics_cleaned.csv")
        self.df = None
        self.raw_df = None
        self.showing_original = False
        self.stats = None
        self.chart_descriptions = {}
        self.sort_column_direction = {}

        self.create_layout()
        self.auto_load_default_data()

    def configure_styles(self):
        self.c_bg = "#F8FAFC"
        self.c_card = "#FFFFFF"
        self.c_primary = "#1E293B"
        self.c_secondary = "#0F766E"
        self.c_sky = "#38BDF8"
        self.c_text = "#1E293B"
        self.c_border = "#E2E8F0"

        self.root.configure(bg=self.c_bg)
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=self.c_bg, borderwidth=0, tabmargins=[4, 4, 4, 0])
        self.style.configure(
            "TNotebook.Tab",
            background="#E2E8F0",
            foreground="#64748B",
            padding=[22, 10],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.c_card), ("active", "#CBD5E1")],
            foreground=[("selected", self.c_secondary), ("active", self.c_primary)],
            expand=[("selected", [1, 1, 1, 0])],
        )
        self.style.configure("TFrame", background=self.c_bg)
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), background=self.c_bg,
                             foreground=self.c_text, borderwidth=1, relief="flat", padding=[12, 6])
        self.style.map("TButton", background=[("active", self.c_sky), ("disabled", self.c_border)],
                       foreground=[("active", "white")])
        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=self.c_sky,
                             foreground="white", relief="flat", padding=[12, 6])
        self.style.map("Primary.TButton", background=[("active", "#0EA5E9"), ("disabled", "#94A3B8")])
        self.style.configure("TLabel", background=self.c_bg, foreground=self.c_text, font=("Segoe UI", 10))
        self.style.configure("Treeview", font=("Segoe UI", 10), background=self.c_card,
                             fieldbackground=self.c_card, rowheight=31, borderwidth=0)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=self.c_bg,
                             foreground=self.c_text, borderwidth=0, relief="flat")
        self.style.map("Treeview", background=[("selected", "#F0F9FF")], foreground=[("selected", "#0284C7")])

    def create_layout(self):
        header_wrap = tk.Frame(self.root, bg=self.c_card,
                               highlightbackground=self.c_border, highlightthickness=1)
        header_wrap.pack(fill=tk.X)

        tk.Frame(header_wrap, bg=self.c_secondary, height=4).pack(fill=tk.X)

        header = tk.Frame(header_wrap, bg=self.c_card, height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_block = tk.Frame(header, bg=self.c_card)
        title_block.pack(expand=True)

        try:
            logo_img = PIL.Image.open("PyPulse.png")
            logo_img = logo_img.resize((140, 33), PIL.Image.Resampling.LANCZOS)
            self._logo_photo = PIL.ImageTk.PhotoImage(logo_img)
            tk.Label(
                title_block,
                image=self._logo_photo,
                bg=self.c_card,
            ).pack(anchor="center", pady=(2, 0))
        except Exception:
            pass

        tk.Label(
            title_block,
            text="Health & Fitness Analytics Dashboard",
            font=("Segoe UI", 10, "bold"),
            fg=self.c_secondary,
            bg=self.c_card,
        ).pack(anchor="center", pady=(0, 0))
        tk.Label(
            title_block,
            text="Integrative Programming Project (Group 4)",
            font=("Segoe UI", 8, "italic"),
            fg="#64748B",
            bg=self.c_card,
        ).pack(anchor="center", pady=(0, 6))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_data = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)
        self.tab_viz = ttk.Frame(self.notebook)
        self.tab_report = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_data, text=" Data Center ")
        self.notebook.add(self.tab_stats, text=" Analytics Dashboard ")
        self.notebook.add(self.tab_viz, text=" Visualization Hub ")
        self.notebook.add(self.tab_report, text=" Summary & Export ")

        self.setup_data_tab()
        self.setup_stats_tab()
        self.setup_viz_tab()
        self.setup_report_tab()

    def _card_hover(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(highlightbackground=self.c_sky))
        widget.bind("<Leave>", lambda e: widget.config(highlightbackground=self.c_border))

    def _clear(self, widget):
        for child in widget.winfo_children():
            child.destroy()

    def _subtitle(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 10), fg="#64748B",
                 bg=self.c_bg, wraplength=900, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

    def _setup_search_placeholder(self, entry):
        self.search_has_placeholder = True
        self.search_val.set(SEARCH_PLACEHOLDER)
        entry.configure(foreground="#94A3B8")

        def on_focus_in(_event):
            if self.search_has_placeholder:
                self.search_val.set("")
                entry.configure(foreground=self.c_text)
                self.search_has_placeholder = False

        def on_focus_out(_event):
            if not self.search_val.get().strip():
                self._show_search_placeholder()

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _show_search_placeholder(self):
        self.search_has_placeholder = True
        self.search_val.set(SEARCH_PLACEHOLDER)
        self.search_entry.configure(foreground="#94A3B8")

    def _clear_search(self):
        self.search_val.set("")
        self.search_has_placeholder = False
        self.search_entry.configure(foreground=self.c_text)
        self.search_entry.focus_set()
        self.filter_treeview()

    def _treeview_from_df(
        self,
        parent,
        dataframe,
        left_align=("activity_type", "gender", "statistic", "relationship", "interpretation", "risk_reason"),
        col_widths=None,
        compact=False,
    ):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0 if compact else 1)

        container = ttk.Frame(parent)
        container.grid(row=0, column=0, sticky="ew" if compact else "nsew", padx=8, pady=8)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=0 if compact else 1)

        vsb = ttk.Scrollbar(container, orient="vertical")
        hsb = ttk.Scrollbar(container, orient="horizontal")
        row_count = max(len(dataframe), 1)
        height = min(row_count, 16) if compact else 10
        tree = ttk.Treeview(container, yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                            selectmode="none", height=height)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        tree.grid(row=0, column=0, sticky="ew" if compact else "nsew")
        if not compact or row_count > height:
            vsb.grid(row=0, column=1, sticky="ns")
        if not compact:
            hsb.grid(row=1, column=0, sticky="ew")

        default_widths = {
            "relationship": 220, "interpretation": 420, "r_val": 80, "expected": 110,
            "activity_type": 130, "risk_reason": 260, "participant_id": 90,
        }
        col_widths = col_widths or {}

        cols = list(dataframe.columns)
        tree["columns"] = cols
        tree["show"] = "headings"
        for col in cols:
            label = COL_LABELS.get(col, col.replace("_", " ").title())
            tree.heading(col, text=label)
            width = col_widths.get(col, default_widths.get(col, 110))
            stretch_cols = ("interpretation", "risk_reason") if not compact else ()
            tree.column(col, width=width, minwidth=70, stretch=col in stretch_cols,
                        anchor="w" if col in left_align else "center")
        for _, row in dataframe.iterrows():
            tree.insert("", "end", values=[format_display_value(c, row[c]) for c in cols])
        return tree

    def setup_data_tab(self):
        self.tab_data.columnconfigure(0, weight=0, minsize=320)
        self.tab_data.columnconfigure(1, weight=1)
        self.tab_data.rowconfigure(0, weight=1)

        ctrl_frame = ttk.Frame(self.tab_data)
        ctrl_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        load_card = tk.Frame(ctrl_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        load_card.pack(fill=tk.X, padx=4, pady=4)
        tk.Label(load_card, text="1. Load Raw Dataset", font=("Segoe UI", 12, "bold"),
                 fg=self.c_primary, bg=self.c_card).pack(anchor="w", padx=15, pady=10)

        ttk.Entry(load_card, textvariable=self.raw_filepath, font=("Segoe UI", 9)).pack(
            fill=tk.X, padx=15, pady=(0, 6))
        ttk.Button(load_card, text="Browse File...", command=self.browse_raw_file).pack(
            anchor="e", padx=15, pady=(0, 12))

        clean_card = tk.Frame(ctrl_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        clean_card.pack(fill=tk.X, padx=4, pady=8)
        tk.Label(clean_card, text="2. Data Preprocessing", font=("Segoe UI", 12, "bold"),
                 fg=self.c_primary, bg=self.c_card).pack(anchor="w", padx=15, pady=10)
        ttk.Button(clean_card, text="Run Clean & Deduplication",
                   command=self.execute_data_cleaning).pack(fill=tk.X, padx=15, pady=10)

        self.btn_view_original = ttk.Button(
            clean_card,
            text="View Original File",
            command=self.toggle_original_preview,
            state="disabled",
        )
        self.btn_view_original.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Label(
            clean_card,
            text="Dates are normalized to YYYY-MM-DD during cleaning.",
            font=("Segoe UI", 8),
            bg=self.c_card,
            fg="#64748B",
        ).pack(anchor="w", padx=15, pady=(0, 8))

        self.clean_stats_frame = tk.Frame(clean_card, bg=self.c_card)
        self.clean_stats_frame.pack(fill=tk.X, padx=15, pady=5)
        self.lbl_orig_rows = tk.Label(self.clean_stats_frame, text="Original Records: N/A",
                                      font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        self.lbl_clean_rows = tk.Label(self.clean_stats_frame, text="Cleaned Records: N/A",
                                       font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        self.lbl_deleted_rows = tk.Label(self.clean_stats_frame, text="Removed Records: N/A",
                                         font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        for lbl in (self.lbl_orig_rows, self.lbl_clean_rows, self.lbl_deleted_rows):
            lbl.pack(anchor="w", pady=2)

        quality_card = tk.Frame(ctrl_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        quality_card.pack(fill=tk.X, padx=4, pady=8)
        tk.Label(quality_card, text="Data Quality Summary", font=("Segoe UI", 12, "bold"),
                 fg=self.c_secondary, bg=self.c_card).pack(anchor="w", padx=15, pady=(12, 8))

        self.quality_stats_frame = tk.Frame(quality_card, bg=self.c_card)
        self.quality_stats_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
        self.lbl_missing_fixed = tk.Label(
            self.quality_stats_frame, text="Missing Values Fixed: N/A",
            font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        self.lbl_dupes_removed = tk.Label(
            self.quality_stats_frame, text="Duplicate Rows Removed: N/A",
            font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        self.lbl_labels_fixed = tk.Label(
            self.quality_stats_frame, text="Inconsistent Labels Fixed: N/A",
            font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        for lbl in (self.lbl_missing_fixed, self.lbl_dupes_removed, self.lbl_labels_fixed):
            lbl.pack(anchor="w", pady=3)

        preview_frame = tk.Frame(self.tab_data, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        preview_header = tk.Frame(preview_frame, bg=self.c_card)
        preview_header.pack(fill=tk.X, padx=12, pady=8)
        self.lbl_preview_title = tk.Label(
            preview_header, text="Cleaned Dataset Preview", font=("Segoe UI", 12, "bold"),
            fg=self.c_primary, bg=self.c_card)
        self.lbl_preview_title.pack(side=tk.LEFT)

        search_frame = tk.Frame(preview_header, bg=self.c_card)
        search_frame.pack(side=tk.RIGHT)
        self.search_val = tk.StringVar()
        self.search_val.trace_add("write", lambda *_: self.filter_treeview())
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_val, width=32, font=("Segoe UI", 9))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self._setup_search_placeholder(self.search_entry)
        ttk.Button(search_frame, text="Clear", width=6, command=self._clear_search).pack(side=tk.LEFT, padx=5)

        tree_container = ttk.Frame(preview_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        self.tree = ttk.Treeview(tree_container, yscrollcommand=vsb.set, xscrollcommand=hsb.set, selectmode="browse")
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree["show"] = "headings"

        for card in (load_card, clean_card, quality_card, preview_frame):
            self._card_hover(card)

    def browse_raw_file(self):
        path = filedialog.askopenfilename(initialdir=".", title="Select Raw CSV File",
                                          filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
        if path:
            self.raw_filepath.set(path)

    def auto_load_default_data(self):
        raw_path = self.raw_filepath.get()
        if not os.path.exists(raw_path):
            return
        try:
            raw_df = pd.read_csv(raw_path)
            self.raw_df = raw_df.copy()
            self.showing_original = True
            self.update_quality_labels(raw_df)
            self.update_cleaning_stats_labels(len(raw_df), "N/A")
            self.lbl_preview_title.config(text="Original Dataset Preview")
            self.populate_treeview(self.raw_df, raw_dates=True)
        except Exception as exc:
            print(f"Error loading default raw data: {exc}")

    def execute_data_cleaning(self):
        raw_path = self.raw_filepath.get()
        cleaned_path = self.cleaned_filepath.get()
        if not os.path.exists(raw_path):
            messagebox.showerror("File Error", f"The raw file '{raw_path}' does not exist.")
            return
        try:
            raw_df = pd.read_csv(raw_path)
            original_len = len(raw_df)
            self.raw_df = raw_df.copy()
            self.showing_original = False
            self.btn_view_original.config(state="normal", text="View Original File")
            self.lbl_preview_title.config(text="Cleaned Dataset Preview")
            self.update_quality_labels(raw_df)
            clean_fitness_data(raw_path, cleaned_path)
            self.df = pd.read_csv(cleaned_path)
            self.df["date"] = pd.to_datetime(self.df["date"])
            self.update_cleaning_stats_labels(original_len, len(self.df))
            self.populate_treeview(self.df)
            self.run_analytics_pipeline()
            messagebox.showinfo(
                "Success",
                f"Cleaning complete. Loaded {len(self.df)} records.\n"
                f"Saved sorted file:\n{cleaned_path}",
            )
        except Exception as exc:
            messagebox.showerror("Error", f"Data cleaning failed:\n{exc}")

    def toggle_original_preview(self):
        if self.raw_df is None:
            return
        if self.showing_original:
            if self.df is not None:
                self.showing_original = False
                self.btn_view_original.config(text="View Original File")
                self.lbl_preview_title.config(text="Cleaned Dataset Preview")
                self.populate_treeview(self.df)
        else:
            self.showing_original = True
            self.btn_view_original.config(text="View Cleaned File")
            self.lbl_preview_title.config(text="Original Dataset Preview")
            self.populate_treeview(self.raw_df, raw_dates=True)

    def update_cleaning_stats_labels(self, original_count, cleaned_count):
        self.lbl_orig_rows.config(text=f"Original Records: {original_count}")
        self.lbl_clean_rows.config(text=f"Cleaned Records: {cleaned_count}")
        if isinstance(original_count, int) and isinstance(cleaned_count, int):
            self.lbl_deleted_rows.config(text=f"Removed Records: {original_count - cleaned_count}")
        else:
            self.lbl_deleted_rows.config(text="Removed Records: N/A")

    def update_quality_labels(self, raw_df):
        if raw_df is None:
            self.lbl_missing_fixed.config(text="Missing Values Fixed: N/A")
            self.lbl_dupes_removed.config(text="Duplicate Rows Removed: N/A")
            self.lbl_labels_fixed.config(text="Inconsistent Labels Fixed: N/A")
            return
        metrics = compute_quality_metrics(raw_df)
        self.lbl_missing_fixed.config(text=f"Missing Values Fixed: {metrics['missing_values']}")
        self.lbl_dupes_removed.config(text=f"Duplicate Rows Removed: {metrics['duplicate_rows']}")
        self.lbl_labels_fixed.config(text=f"Inconsistent Labels Fixed: {metrics['inconsistent_labels']}")

    def populate_treeview(self, dataframe, raw_dates=False):
        self.tree.delete(*self.tree.get_children())
        cols = list(dataframe.columns)
        self.tree["columns"] = cols
        for col in cols:
            label = COL_LABELS.get(col, col.replace("_", " ").title())
            self.tree.heading(col, text=label, command=lambda c=col: self.sort_treeview_column(c))
            width = {
                "participant_id": 90,
                "date": 150,
                "gender": 80,
                "activity_type": 130,
                "avg_heart_rate": 140,
                "calories_burned": 165,
                "daily_steps": 110,
                "sleep_hours": 100,
            }.get(col, 120)
            self.tree.column(col, width=width, minwidth=width, anchor="center", stretch=True)
        for _, row in dataframe.iterrows():
            values = []
            for c in cols:
                val = row[c]
                if c == "date":
                    if isinstance(val, pd.Timestamp):
                        val = val.strftime("%Y-%m-%d")
                    elif not raw_dates and isinstance(val, str) and len(val) >= 10:
                        val = val[:10]
                else:
                    val = format_display_value(c, val)
                values.append(val)
            self.tree.insert("", "end", values=values)

    def filter_treeview(self):
        active_df = self.raw_df if self.showing_original and self.raw_df is not None else self.df
        if active_df is None:
            return
        raw_dates = self.showing_original
        if self.search_has_placeholder:
            self.populate_treeview(active_df, raw_dates=raw_dates)
            return
        query = self.search_val.get().lower().strip()
        if not query or query == SEARCH_PLACEHOLDER.lower():
            self.populate_treeview(active_df, raw_dates=raw_dates)
            return
        mask = active_df.astype(str).apply(
            lambda row: row.str.lower().str.contains(query, na=False).any(), axis=1
        )
        filtered = active_df[mask]
        if filtered.empty:
            self.tree.delete(*self.tree.get_children())
            return
        self.populate_treeview(filtered, raw_dates=raw_dates)

    def sort_treeview_column(self, col):
        direction = self.sort_column_direction.get(col, False)
        self.sort_column_direction[col] = not direction
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda t: float(t[0].replace(",", "")), reverse=direction)
        except ValueError:
            items.sort(reverse=direction)
        for index, (_, item_id) in enumerate(items):
            self.tree.move(item_id, "", index)
        for c in self.tree["columns"]:
            label = COL_LABELS.get(c, c.replace("_", " ").title())
            arrow = ""
            if c == col:
                arrow = " ▲" if not direction else " ▼"
            self.tree.heading(c, text=label + arrow)

    def run_analytics_pipeline(self):
        if self.df is None:
            return
        self.stats = compute_all_statistics(self.df)
        show_all_charts(self.df, save_dir="charts/")
        try:
            self.chart_descriptions = generate_chart_descriptions(self.df, self.stats)
        except Exception as exc:
            print(f"Could not generate chart descriptions: {exc}")
            self.chart_descriptions = {}
        self.populate_stats_dashboard()
        self.update_chart_view()
        self.populate_summary_report()

    def setup_stats_tab(self):
        self.stats_notebook = ttk.Notebook(self.tab_stats)
        self.stats_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.stats_insights = ttk.Frame(self.stats_notebook)
        self.stats_desc = ttk.Frame(self.stats_notebook)
        self.stats_cards = ttk.Frame(self.stats_notebook)
        self.stats_corr = ttk.Frame(self.stats_notebook)
        self.stats_group = ttk.Frame(self.stats_notebook)
        self.stats_risk = ttk.Frame(self.stats_notebook)
        for frame in (self.stats_insights, self.stats_desc, self.stats_cards, self.stats_corr, self.stats_group, self.stats_risk):
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        self.stats_notebook.add(self.stats_insights, text=" Stakeholder Insights ")
        self.stats_notebook.add(self.stats_desc, text=" Descriptive Statistics ")
        self.stats_notebook.add(self.stats_cards, text=" Health Benchmarks ")
        self.stats_notebook.add(self.stats_corr, text=" Correlation Analysis ")
        self.stats_notebook.add(self.stats_group, text=" Summaries by Group ")
        self.stats_notebook.add(self.stats_risk, text=" At-Risk Participants ")

    def populate_stats_dashboard(self):
        if self.stats is None:
            return
        self.draw_stakeholder_insights()
        self.draw_descriptive_stats_table()
        self.draw_benchmark_cards()
        self.draw_correlation_table()
        self.draw_group_summary_tables()
        self.draw_at_risk_table()

    def _metric_chip(self, parent, value, caption, color, bg):
        chip = tk.Frame(parent, bg=bg)
        tk.Label(chip, text=value, font=("Segoe UI", 15, "bold"), fg=color, bg=bg,
                 anchor="w").pack(anchor="w")
        tk.Label(chip, text=caption, font=("Segoe UI", 9), fg="#64748B", bg=bg,
                 anchor="w").pack(anchor="w")
        return chip

    def _small_info_card(self, parent, title, value, caption, color):
        card = tk.Frame(parent, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        self._card_hover(card)
        tk.Frame(card, bg=color, height=4).pack(fill=tk.X)
        tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), fg=self.c_primary,
                 bg=self.c_card, anchor="w").pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(card, text=value, font=("Segoe UI", 20, "bold"), fg=color,
                 bg=self.c_card, anchor="w").pack(anchor="w", padx=14)
        tk.Label(card, text=caption, font=("Segoe UI", 9), fg="#64748B", bg=self.c_card,
                 anchor="w", justify="left", wraplength=190).pack(anchor="w", padx=14, pady=(4, 12))
        return card

    def draw_stakeholder_insights(self):
        self._clear(self.stats_insights)
        insights = build_stakeholder_insights(self.stats)
        eff = self.stats["activity_effectiveness"]
        step = self.stats["step_benchmark"]
        desc = self.stats["descriptive"]
        pcts = self.stats["percentages"]
        at_risk = self.stats["at_risk_participants"]
        top_activity = str(self.stats["activity_frequency"].iloc[0]["activity_type"])

        panels = [
            ("Health-Conscious Individuals", insights["individuals"], "#0F766E", "#ECFDF5", [
                (f"{desc['daily_steps']['mean']:,.0f}", "avg steps / session"),
                (f"{desc['sleep_hours']['mean']:.1f} h", "avg sleep"),
                (f"{pcts['steps_benchmark_pct']:.0f}%", "sessions hit step goal"),
                (top_activity, "most logged activity"),
            ]),
            ("Athletic Trainers & Coaches", insights["coaches"], "#4C72B0", "#EFF6FF", [
                (f"{eff['highest_avg_calories']['avg_calories']:.0f} kcal",
                 f"top burn · {eff['highest_avg_calories']['activity_type']}"),
                (f"{eff['most_efficient']['calories_per_minute']:.1f}/min",
                 f"most efficient · {eff['most_efficient']['activity_type']}"),
                (str(eff['lowest_avg_calories']['activity_type']), "best for recovery"),
            ]),
            ("Wellness Administrators", insights["administrators"], "#C44E52", "#FEF2F2", [
                (f"{len(at_risk)}/{step['participants_total']}", "flagged participants"),
                (f"{pcts['low_sleep_pct']:.0f}%", "short-sleep sessions"),
                (f"{100 - step['participant_pct_met']:.0f}%", "below step goal"),
            ]),
        ]
        wrapper = ttk.Frame(self.stats_insights)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        wrapper.columnconfigure(0, weight=1)
        for idx, (title, body, color, tint, chips) in enumerate(panels):
            wrapper.rowconfigure(idx, weight=1)
            card = tk.Frame(wrapper, bg=tint, highlightbackground=color, highlightthickness=1)
            card.grid(row=idx, column=0, sticky="nsew", pady=5)
            self._card_hover(card)

            tk.Frame(card, bg=color, width=6).pack(side=tk.LEFT, fill=tk.Y)

            block = tk.Frame(card, bg=tint)
            block.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=22, pady=14)

            tk.Label(block, text=title, font=("Segoe UI", 15, "bold"), fg=color, bg=tint,
                     anchor="w").pack(anchor="w", pady=(0, 4))
            body_lbl = tk.Label(block, text=body, font=("Segoe UI", 11), fg=self.c_text, bg=tint,
                                 anchor="w", justify="left", wraplength=980)
            body_lbl.pack(anchor="w", fill=tk.X, pady=(0, 12))
            block.bind("<Configure>",
                       lambda e, lbl=body_lbl: lbl.config(wraplength=max(e.width - 20, 400)))

            chip_row = tk.Frame(block, bg=tint)
            chip_row.pack(anchor="w", fill=tk.X)
            for c_idx, (value, caption) in enumerate(chips):
                if c_idx:
                    tk.Frame(chip_row, bg=color, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=18, pady=2)
                self._metric_chip(chip_row, value, caption, color, tint).pack(side=tk.LEFT)

    def draw_descriptive_stats_table(self):
        self._clear(self.stats_desc)
        self._subtitle(self.stats_desc, "Quick statistical profile for each tracked health variable.")

        desc = self.stats["descriptive"]
        variables = [
            ("Duration", "duration_minutes", "min", "#0F766E"),
            ("Calories", "calories_burned", "kcal", "#55A868"),
            ("Daily Steps", "daily_steps", "steps", "#4C72B0"),
            ("Heart Rate", "avg_heart_rate", "bpm", "#C44E52"),
            ("Sleep", "sleep_hours", "hrs", "#8172B2"),
        ]

        grid = ttk.Frame(self.stats_desc)
        grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
        grid.columnconfigure((0, 1, 2), weight=1, uniform="desc")
        grid.rowconfigure((0, 1), weight=1, uniform="desc")

        for idx, (title, key, unit, color) in enumerate(variables):
            row, col = divmod(idx, 3)
            values = desc[key]
            card = tk.Frame(grid, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            self._card_hover(card)
            tk.Frame(card, bg=color, height=5).pack(fill=tk.X)
            tk.Label(card, text=title, font=("Segoe UI", 13, "bold"), fg=color, bg=self.c_card,
                     anchor="w").pack(anchor="w", padx=16, pady=(14, 4))
            tk.Label(card, text=f"{values['mean']:,.2f} {unit}", font=("Segoe UI", 21, "bold"),
                     fg=self.c_primary, bg=self.c_card, anchor="w").pack(anchor="w", padx=16)
            tk.Label(card, text="mean", font=("Segoe UI", 9), fg="#64748B", bg=self.c_card,
                     anchor="w").pack(anchor="w", padx=16, pady=(0, 10))

            details = tk.Frame(card, bg=self.c_card)
            details.pack(fill=tk.X, padx=16, pady=(0, 14))
            detail_rows = [
                ("Median", f"{values['median']:,.2f}"),
                ("Mode", f"{values['mode']:,.2f}" if values["mode"] is not None else "N/A"),
                ("Std Dev", f"{values['std']:,.2f}"),
                ("Range", f"{values['min']:,.2f} - {values['max']:,.2f}"),
            ]
            for label, value in detail_rows:
                line = tk.Frame(details, bg=self.c_card)
                line.pack(fill=tk.X, pady=1)
                tk.Label(line, text=label, font=("Segoe UI", 9, "bold"), fg="#475569",
                         bg=self.c_card, anchor="w", width=9).pack(side=tk.LEFT)
                tk.Label(line, text=value, font=("Segoe UI", 9), fg=self.c_text,
                         bg=self.c_card, anchor="w").pack(side=tk.LEFT)

    def draw_benchmark_cards(self):
        self._clear(self.stats_cards)
        self._subtitle(self.stats_cards, "Session-level percentages against recognized health thresholds.")
        cards_container = ttk.Frame(self.stats_cards)
        cards_container.pack(fill=tk.X, padx=12, pady=(0, 4))

        pcts = self.stats["percentages"]
        step = self.stats["step_benchmark"]
        corr = self.stats["correlation_matrix"]
        card_data = [
            ("High Intensity", f"{pcts['high_intensity_pct']}%",
             f"sessions with heart rate ≥ {HIGH_INTENSITY_HR} bpm", "#C44E52"),
            ("Short Sleep", f"{pcts['low_sleep_pct']}%",
             f"sessions following under {LOW_SLEEP_HOURS} hrs of sleep", "#E2B13C"),
            ("High Calorie Burn", f"{pcts['high_calorie_pct']}%",
             f"sessions burning ≥ {HIGH_CALORIE} kcal", "#55A868"),
            ("Step Benchmark", f"{pcts['steps_benchmark_pct']}%",
             f"sessions reaching {STEP_BENCHMARK:,}+ daily steps", "#4C72B0"),
            ("Long Sessions", f"{pcts['long_session_pct']}%",
             f"sessions lasting {LONG_SESSION_MIN}+ minutes", "#8172B2"),
        ]

        cards_container.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="equal")
        for idx, (title, val, desc, color) in enumerate(card_data):
            card = tk.Frame(cards_container, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            card.grid(row=0, column=idx, sticky="nsew", padx=6, pady=4)
            self._card_hover(card)
            tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), fg=self.c_primary, bg=self.c_card).pack(
                anchor="w", padx=15, pady=(15, 5))
            tk.Label(card, text=val, font=("Segoe UI", 24, "bold"), fg=color, bg=self.c_card).pack(anchor="w", padx=15)
            tk.Label(card, text=desc, font=("Segoe UI", 9), fg="#64748B", bg=self.c_card,
                     wraplength=180, justify="left").pack(anchor="w", padx=15, pady=(5, 15))

        r_sleep_hr = corr.loc["sleep_hours", "avg_heart_rate"]
        takeaways = [
            ("Intensity is healthy", "#C44E52",
             f"{pcts['high_intensity_pct']:.0f}% of sessions reach the vigorous zone "
             f"(HR ≥ {HIGH_INTENSITY_HR} bpm) and {pcts['high_calorie_pct']:.0f}% burn at least {HIGH_CALORIE} kcal."),
            ("Steps are the weak spot", "#4C72B0",
             f"Only {step['participant_pct_met']:.0f}% of participants average the {STEP_BENCHMARK:,}-step goal. "
             f"That is a participant-level measure; the blue KPI above is session-level."),
            ("Sleep drives recovery", "#E2B13C",
             f"{pcts['low_sleep_pct']:.0f}% of sessions follow nights under {LOW_SLEEP_HOURS} hrs of sleep; "
             f"sleep and heart rate move together (r = {r_sleep_hr:.2f}), so short sleep raises heart rate during activity."),
            ("Endurance holds up", "#8172B2",
             f"{pcts['long_session_pct']:.0f}% of sessions run {LONG_SESSION_MIN} minutes or longer, "
             f"showing the cohort sustains meaningful workout durations."),
        ]

        tk.Label(self.stats_cards, text="What these benchmarks tell us", font=("Segoe UI", 12, "bold"),
                 fg=self.c_secondary, bg=self.c_bg, anchor="w").pack(anchor="w", padx=18, pady=(10, 2))

        grid = ttk.Frame(self.stats_cards)
        grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
        grid.columnconfigure((0, 1), weight=1, uniform="insight")
        grid.rowconfigure((0, 1), weight=1, uniform="insight")
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (heading, accent, body), (r, c) in zip(takeaways, positions):
            mini = tk.Frame(grid, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            mini.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            self._card_hover(mini)
            tk.Frame(mini, bg=accent, width=6).pack(side=tk.LEFT, fill=tk.Y)
            inner = tk.Frame(mini, bg=self.c_card)
            inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=12)
            tk.Label(inner, text=heading, font=("Segoe UI", 12, "bold"), fg=accent,
                     bg=self.c_card, anchor="w").pack(anchor="w", pady=(0, 6))
            body_lbl = tk.Label(inner, text=body, font=("Segoe UI", 10), fg="#475569",
                                bg=self.c_card, anchor="w", justify="left", wraplength=420)
            body_lbl.pack(anchor="w", fill=tk.X)
            inner.bind("<Configure>",
                       lambda e, lbl=body_lbl: lbl.config(wraplength=max(e.width - 16, 240)))

    def draw_correlation_table(self):
        self._clear(self.stats_corr)
        self._subtitle(self.stats_corr, "Pearson correlations supporting activity, sleep, and cardiovascular patterns.")

        corr = self.stats["correlation_matrix"]
        cards = [
            ("Duration vs Calories", corr.loc["duration_minutes", "calories_burned"],
             "moderate positive", "Longer workouts usually burn more calories.", "#55A868"),
            ("Sleep vs Heart Rate", corr.loc["sleep_hours", "avg_heart_rate"],
             "weak negative", "Shorter sleep tends to align with higher workout heart rate.", "#E2B13C"),
            ("Steps vs Calories", corr.loc["daily_steps", "calories_burned"],
             "very weak positive", "Daily steps help, but activity type still explains much of calorie burn.", "#4C72B0"),
        ]

        grid = ttk.Frame(self.stats_corr)
        grid.pack(fill=tk.X, anchor="n", padx=12, pady=(0, 10))
        grid.columnconfigure((0, 1, 2), weight=1, uniform="corr")
        for idx, (title, value, label, body, color) in enumerate(cards):
            card = tk.Frame(grid, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            card.grid(row=0, column=idx, sticky="nsew", padx=6, pady=6)
            self._card_hover(card)
            tk.Frame(card, bg=color, height=5).pack(fill=tk.X)
            tk.Label(card, text=title, font=("Segoe UI", 13, "bold"), fg=color,
                     bg=self.c_card, anchor="w").pack(anchor="w", padx=18, pady=(18, 8))
            tk.Label(card, text=f"r = {value:.3f}", font=("Segoe UI", 28, "bold"), fg=self.c_primary,
                     bg=self.c_card, anchor="w").pack(anchor="w", padx=18)
            tk.Label(card, text=label, font=("Segoe UI", 10, "bold"), fg="#64748B",
                     bg=self.c_card, anchor="w").pack(anchor="w", padx=18, pady=(0, 14))
            body_lbl = tk.Label(card, text=body, font=("Segoe UI", 11), fg="#334155",
                                bg=self.c_card, anchor="w", justify="left", wraplength=280)
            body_lbl.pack(anchor="w", fill=tk.X, padx=18, pady=(0, 18))
            card.bind("<Configure>",
                      lambda e, lbl=body_lbl: lbl.config(wraplength=max(e.width - 44, 220)))

    def _group_summary_view(self, parent, dataframe, cards, col_widths=None):
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, padx=12, pady=(10, 2))
        header.columnconfigure((0, 1, 2), weight=1, uniform="summary_cards")
        for idx, (title, value, caption, color) in enumerate(cards):
            card = self._small_info_card(header, title, value, caption, color)
            card.grid(row=0, column=idx, sticky="nsew", padx=6)

        table_frame = tk.Frame(parent, bg=self.c_card,
                               highlightbackground=self.c_border, highlightthickness=1)
        table_frame.pack(fill=tk.X, padx=18, pady=12)
        self._treeview_from_df(table_frame, dataframe, col_widths=col_widths, compact=True)

    def draw_group_summary_tables(self):
        self._clear(self.stats_group)
        sub_notebook = ttk.Notebook(self.stats_group)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        tab_act = ttk.Frame(sub_notebook)
        tab_eff = ttk.Frame(sub_notebook)
        tab_gen = ttk.Frame(sub_notebook)
        for tab in (tab_act, tab_eff, tab_gen):
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
        sub_notebook.add(tab_act, text=" By Avg Calories ")
        sub_notebook.add(tab_eff, text=" By Efficiency ")
        sub_notebook.add(tab_gen, text=" By Gender ")

        activity = self.stats["activity_summary"]
        efficient = self.stats["activity_by_efficiency"]
        gender = self.stats["gender_summary"]
        top_activity = activity.iloc[0]
        top_eff = efficient.iloc[0]
        top_gender = gender.sort_values("avg_calories", ascending=False).iloc[0]
        common_widths = {
            "activity_type": 130,
            "sessions": 85,
            "total_calories": 120,
            "avg_calories": 115,
            "avg_duration": 110,
            "avg_steps": 105,
            "avg_heart_rate": 115,
            "avg_sleep": 110,
            "calories_per_minute": 135,
        }

        self._group_summary_view(tab_act, activity, [
            ("Top Burn", f"{top_activity['avg_calories']:.0f} kcal", str(top_activity["activity_type"]), "#55A868"),
            ("Logged Sessions", f"{int(activity['sessions'].sum()):,}", "total activity records", "#4C72B0"),
            ("Activity Types", f"{len(activity)}", "categories tracked", "#0F766E"),
        ], col_widths=common_widths)

        self._group_summary_view(tab_eff, efficient, [
            ("Most Efficient", f"{top_eff['calories_per_minute']:.1f}/min", str(top_eff["activity_type"]), "#C44E52"),
            ("Avg Duration", f"{top_eff['avg_duration']:.0f} min", "for the top activity", "#8172B2"),
            ("Avg Calories", f"{top_eff['avg_calories']:.0f} kcal", "for the top activity", "#55A868"),
        ], col_widths=common_widths)

        self._group_summary_view(tab_gen, gender, [
            ("Higher Avg Burn", f"{top_gender['avg_calories']:.0f} kcal", str(top_gender["gender"]), "#55A868"),
            ("Female Logs", f"{int(gender.loc[gender['gender'] == 'Female', 'sessions'].iloc[0]):,}", "sessions", "#C44E52"),
            ("Male Logs", f"{int(gender.loc[gender['gender'] == 'Male', 'sessions'].iloc[0]):,}", "sessions", "#4C72B0"),
        ], col_widths={
            "gender": 120,
            "sessions": 95,
            "total_calories": 140,
            "avg_calories": 130,
            "avg_steps": 125,
            "avg_sleep": 125,
            "avg_heart_rate": 135,
        })

    def draw_at_risk_table(self):
        self._clear(self.stats_risk)
        at_risk = self.stats["at_risk_participants"]
        count = len(at_risk)
        self._subtitle(
            self.stats_risk,
            f"Participants averaging below {STEP_BENCHMARK:,} steps or {LOW_SLEEP_HOURS} hrs sleep — "
            f"{count} flagged for wellness administrator follow-up.",
        )
        table_frame = tk.Frame(self.stats_risk, bg=self.c_card,
                               highlightbackground=self.c_border, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        if count:
            cols = ["participant_id", "avg_steps", "avg_sleep", "total_sessions", "risk_reason"]
            self._treeview_from_df(table_frame, at_risk[cols], compact=True, col_widths={
                "participant_id": 110,
                "avg_steps": 130,
                "avg_sleep": 130,
                "total_sessions": 130,
                "risk_reason": 260,
            })
        else:
            tk.Label(table_frame, text="No participants flagged at current thresholds.",
                     font=("Segoe UI", 11, "italic"), fg="#64748B", bg=self.c_card).pack(pady=40)

    def setup_viz_tab(self):
        toolbar = tk.Frame(self.tab_viz, bg=self.c_primary, height=46)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        tk.Label(toolbar, text="CHARTS", font=("Segoe UI", 9, "bold"),
                 fg="#64748B", bg=self.c_primary).pack(side=tk.LEFT, padx=(15, 8))

        chart_buttons = [
            ("Calories by Activity", "bar_calories_by_activity.png", "bar"),
            ("Monthly Trend", "line_monthly_calories.png", "line"),
            ("Activity Share", "pie_activity_distribution.png", "pie"),
            ("Sleep Distribution", "histogram_sleep_hours.png", "histogram"),
            ("Steps vs Calories", "scatter_steps_vs_calories.png", "scatter"),
        ]
        self.chart_meta = {fn: (title, key) for title, fn, key in chart_buttons}
        self.active_chart_file = tk.StringVar(value=chart_buttons[0][1])
        self.viz_buttons = {}
        for title, filename, _key in chart_buttons:
            btn = tk.Button(toolbar, text=title, font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
                            padx=14, command=lambda f=filename: self.select_active_chart(f))
            btn.pack(side=tk.LEFT, padx=3, pady=6, fill=tk.Y)
            self.viz_buttons[filename] = btn

        title_bar = tk.Frame(self.tab_viz, bg=self.c_card,
                             highlightbackground=self.c_border, highlightthickness=1)
        title_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        tk.Frame(title_bar, bg=self.c_secondary, width=6).pack(side=tk.LEFT, fill=tk.Y)
        self.lbl_chart_title = tk.Label(title_bar, text="", font=("Segoe UI", 13, "bold"),
                                        fg=self.c_primary, bg=self.c_card, anchor="w")
        self.lbl_chart_title.pack(side=tk.LEFT, padx=12, pady=8)

        desc_panel = tk.Frame(self.tab_viz, bg="#F1F5F9",
                              highlightbackground=self.c_border, highlightthickness=1)
        desc_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(desc_panel, text="INSIGHT", font=("Segoe UI", 10, "bold"),
                 fg=self.c_secondary, bg="#F1F5F9").pack(anchor="w", padx=16, pady=(10, 0))
        self.lbl_chart_desc = tk.Label(desc_panel, text="", font=("Segoe UI", 13),
                                       fg="#334155", bg="#F1F5F9", anchor="w", justify="left",
                                       wraplength=1180)
        self.lbl_chart_desc.pack(anchor="w", fill=tk.X, padx=16, pady=(4, 14))
        desc_panel.bind("<Configure>",
                        lambda e: self.lbl_chart_desc.config(wraplength=max(e.width - 28, 400)))

        self.chart_container = tk.Frame(self.tab_viz, bg=self.c_card,
                                        highlightbackground=self.c_border, highlightthickness=1)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.lbl_chart = tk.Label(self.chart_container, bg=self.c_card)
        self.lbl_chart.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.chart_container.bind("<Configure>", lambda *_: self.load_visualization_images())

        self.update_chart_view()

    def _highlight_active_button(self):
        active = self.active_chart_file.get()
        for filename, btn in self.viz_buttons.items():
            if filename == active:
                btn.config(bg=self.c_sky, fg="white", activebackground=self.c_sky,
                           activeforeground="white")
            else:
                btn.config(bg=self.c_primary, fg="#94A3B8", activebackground="#0F172A",
                           activeforeground="white")

    def select_active_chart(self, filename):
        self.active_chart_file.set(filename)
        self.update_chart_view()

    def update_chart_view(self):
        if not hasattr(self, "lbl_chart_title"):
            return
        filename = self.active_chart_file.get()
        title, key = self.chart_meta.get(filename, (filename, None))
        self.lbl_chart_title.config(text=title)
        self._highlight_active_button()
        insight = self.chart_descriptions.get(key, "") if key else ""
        self.lbl_chart_desc.config(
            text=insight or "Load and clean a dataset to generate chart insights."
        )
        self.load_visualization_images()

    def load_visualization_images(self):
        image_path = os.path.join("charts", self.active_chart_file.get())
        width = max(self.chart_container.winfo_width() - 40, 700)
        height = max(self.chart_container.winfo_height() - 40, 360)
        if self.df is not None and os.path.exists(image_path):
            try:
                img = PIL.Image.open(image_path)
                img.thumbnail((width, height), PIL.Image.Resampling.LANCZOS)
                photo = PIL.ImageTk.PhotoImage(img)
                self.lbl_chart.config(image=photo, text="")
                self.lbl_chart.image = photo
            except Exception as exc:
                self.lbl_chart.config(text=f"Error displaying image: {exc}", image="")
        else:
            self.lbl_chart.config(
                text="Charts not found. Load and clean a dataset first.",
                font=("Segoe UI", 11, "italic"), fg="#64748B", image=""
            )

    def setup_report_tab(self):
        self.tab_report.columnconfigure(0, weight=1)
        self.tab_report.rowconfigure(0, weight=1)
        self.txt_report = scrolledtext.ScrolledText(self.tab_report, wrap=tk.WORD, font=("Consolas", 10),
                                                    bg=self.c_card, fg=self.c_text, relief="solid", bd=1)
        self.txt_report.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 8))

        actions = ttk.Frame(self.tab_report)
        actions.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        ttk.Button(actions, text="Copy Report", command=self.copy_report_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Save as TXT", command=self.export_report_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Export Cleaned CSV", command=self.export_cleaned_csv).pack(side=tk.RIGHT, padx=5)

    def populate_summary_report(self):
        if self.stats is None:
            self.txt_report.delete("1.0", tk.END)
            self.txt_report.insert(tk.END, "Load cleaned data to generate the report.")
            return
        report = build_summary_report(
            self.stats, self.df, self.raw_filepath.get(), self.cleaned_filepath.get()
        )
        self.txt_report.delete("1.0", tk.END)
        self.txt_report.insert(tk.END, report)

    def copy_report_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.txt_report.get("1.0", tk.END))
        messagebox.showinfo("Clipboard", "Report copied.")

    def export_report_txt(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")),
                                                 title="Save Summary Report")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(self.txt_report.get("1.0", tk.END))
            messagebox.showinfo("Success", f"Report saved to:\n{file_path}")

    def export_cleaned_csv(self):
        if self.df is None:
            messagebox.showerror("Export Error", "No cleaned data available.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")),
                                                 title="Export Cleaned Dataset")
        if file_path:
            self.df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Dataset exported to:\n{file_path}")


def main():
    root = tk.Tk()
    root.option_add("*font", "SegoeUI 10")
    PyPulseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
