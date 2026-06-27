import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import PIL.Image
import PIL.ImageTk

from cleaning import clean_fitness_data
from fitness_analytics_stats import (
    compute_all_statistics,
    build_summary_report,
    COL_LABELS,
    NUMERIC_COLS,
    STEP_BENCHMARK,
    HIGH_INTENSITY_HR,
    LOW_SLEEP_HOURS,
    HIGH_CALORIE,
    LONG_SESSION_MIN,
)
from fitness_analytics_viz import show_all_charts


class PyPulseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPulse: Health & Fitness Tracking Analytics")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        self.style = ttk.Style()
        self.configure_styles()

        self.raw_filepath = tk.StringVar(value="Group4_FitnessAnalytics_raw.csv")
        self.cleaned_filepath = tk.StringVar(value="Group4_FitnessAnalytics_cleaned.csv")
        self.df = None
        self.stats = None
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
        self.style.configure("TNotebook", background=self.c_bg, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.c_bg, foreground="#64748B",
                             padding=[18, 8], font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab", background=[("selected", self.c_bg)], foreground=[("selected", self.c_sky)])
        self.style.configure("TFrame", background=self.c_bg)
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), background=self.c_bg,
                             foreground=self.c_text, borderwidth=1, relief="flat", padding=[12, 6])
        self.style.map("TButton", background=[("active", self.c_sky), ("disabled", self.c_border)],
                       foreground=[("active", "white")])
        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=self.c_sky,
                             foreground="white", relief="flat", padding=[12, 6])
        self.style.map("Primary.TButton", background=[("active", "#0EA5E9"), ("disabled", "#94A3B8")])
        self.style.configure("TLabel", background=self.c_bg, foreground=self.c_text, font=("Segoe UI", 10))
        self.style.configure("Treeview", font=("Segoe UI", 9), background=self.c_card,
                             fieldbackground=self.c_card, rowheight=26, borderwidth=0)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background=self.c_bg,
                             foreground=self.c_text, borderwidth=0, relief="flat")
        self.style.map("Treeview", background=[("selected", "#F0F9FF")], foreground=[("selected", "#0284C7")])

    def create_layout(self):
        header = tk.Frame(self.root, bg=self.c_card, height=65,
                          highlightbackground=self.c_border, highlightthickness=1)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="PyPulse Health & Fitness Analytics Dashboard",
                 font=("Segoe UI", 15, "bold"), fg=self.c_primary, bg=self.c_card).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(header, text="Integrative Programming Project (Group 4)",
                 font=("Segoe UI", 10, "italic"), fg="#64748B", bg=self.c_card).pack(side=tk.LEFT, padx=10, pady=20)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        widget.bind("<Enter>", lambda e: widget.config(highlightbackground=self.c_sky, highlightthickness=1.5))
        widget.bind("<Leave>", lambda e: widget.config(highlightbackground=self.c_border, highlightthickness=1))

    def _clear(self, widget):
        for child in widget.winfo_children():
            child.destroy()

    def _section_header(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 13, "bold"),
                 fg=self.c_primary, bg=self.c_bg).pack(anchor="w", padx=20, pady=15)

    def _treeview_from_df(self, parent, dataframe, left_align=("activity_type", "gender", "statistic")):
        tree = ttk.Treeview(parent, selectmode="none")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        cols = list(dataframe.columns)
        tree["columns"] = cols
        tree["show"] = "headings"
        for col in cols:
            label = COL_LABELS.get(col, col.replace("_", " ").title())
            tree.heading(col, text=label)
            tree.column(col, width=110, anchor="w" if col in left_align else "center")
        for _, row in dataframe.iterrows():
            tree.insert("", "end", values=[row[c] for c in cols])
        return tree

    def setup_data_tab(self):
        self.tab_data.columnconfigure(0, weight=1)
        self.tab_data.columnconfigure(1, weight=3)
        self.tab_data.rowconfigure(0, weight=1)

        ctrl_frame = ttk.Frame(self.tab_data)
        ctrl_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        load_card = tk.Frame(ctrl_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        load_card.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(load_card, text="1. Load Raw Dataset", font=("Segoe UI", 12, "bold"),
                 fg=self.c_primary, bg=self.c_card).pack(anchor="w", padx=15, pady=10)

        file_frame = tk.Frame(load_card, bg=self.c_card)
        file_frame.pack(fill=tk.X, padx=15, pady=5)
        ttk.Entry(file_frame, textvariable=self.raw_filepath, font=("Segoe UI", 9)).pack(
            fill=tk.X, side=tk.LEFT, expand=True, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_raw_file).pack(side=tk.RIGHT, padx=5, pady=5)

        clean_card = tk.Frame(ctrl_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        clean_card.pack(fill=tk.X, padx=5, pady=10)
        tk.Label(clean_card, text="2. Data Preprocessing", font=("Segoe UI", 12, "bold"),
                 fg=self.c_primary, bg=self.c_card).pack(anchor="w", padx=15, pady=10)
        ttk.Button(clean_card, text="Run Clean & Deduplication",
                   command=self.execute_data_cleaning).pack(fill=tk.X, padx=15, pady=10)

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

        preview_frame = tk.Frame(self.tab_data, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        preview_header = tk.Frame(preview_frame, bg=self.c_card)
        preview_header.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(preview_header, text="Cleaned Dataset Preview", font=("Segoe UI", 12, "bold"),
                 fg=self.c_primary, bg=self.c_card).pack(side=tk.LEFT)

        search_frame = tk.Frame(preview_header, bg=self.c_card)
        search_frame.pack(side=tk.RIGHT)
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 9, "bold"),
                 bg=self.c_card, fg="#475569").pack(side=tk.LEFT, padx=5)
        self.search_val = tk.StringVar()
        self.search_val.trace_add("write", lambda *_: self.filter_treeview())
        ttk.Entry(search_frame, textvariable=self.search_val, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", width=6,
                   command=lambda: self.search_val.set("")).pack(side=tk.LEFT, padx=5)

        tree_container = ttk.Frame(preview_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        self.tree = ttk.Treeview(tree_container, yscrollcommand=vsb.set, xscrollcommand=hsb.set, selectmode="browse")
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree["show"] = "headings"

        for card in (load_card, clean_card, preview_frame):
            self._card_hover(card)

    def browse_raw_file(self):
        path = filedialog.askopenfilename(initialdir=".", title="Select Raw CSV File",
                                          filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
        if path:
            self.raw_filepath.set(path)

    def auto_load_default_data(self):
        if not os.path.exists(self.cleaned_filepath.get()):
            return
        try:
            self.df = pd.read_csv(self.cleaned_filepath.get())
            self.df["date"] = pd.to_datetime(self.df["date"])
            orig_len = len(pd.read_csv(self.raw_filepath.get())) if os.path.exists(self.raw_filepath.get()) else "N/A"
            self.update_cleaning_stats_labels(orig_len, len(self.df))
            self.populate_treeview(self.df)
            self.run_analytics_pipeline()
        except Exception as exc:
            print(f"Error loading default cleaned data: {exc}")

    def execute_data_cleaning(self):
        raw_path = self.raw_filepath.get()
        cleaned_path = self.cleaned_filepath.get()
        if not os.path.exists(raw_path):
            messagebox.showerror("File Error", f"The raw file '{raw_path}' does not exist.")
            return
        try:
            original_len = len(pd.read_csv(raw_path))
            clean_fitness_data(raw_path, cleaned_path)
            self.df = pd.read_csv(cleaned_path)
            self.df["date"] = pd.to_datetime(self.df["date"])
            self.update_cleaning_stats_labels(original_len, len(self.df))
            self.populate_treeview(self.df)
            self.run_analytics_pipeline()
            messagebox.showinfo("Success", f"Cleaning complete. Loaded {len(self.df)} records.")
        except Exception as exc:
            messagebox.showerror("Error", f"Data cleaning failed:\n{exc}")

    def update_cleaning_stats_labels(self, original_count, cleaned_count):
        self.lbl_orig_rows.config(text=f"Original Records: {original_count}")
        self.lbl_clean_rows.config(text=f"Cleaned Records: {cleaned_count}")
        if isinstance(original_count, int):
            self.lbl_deleted_rows.config(text=f"Removed Records: {original_count - cleaned_count}")
        else:
            self.lbl_deleted_rows.config(text="Removed Records: N/A")

    def populate_treeview(self, dataframe):
        self.tree.delete(*self.tree.get_children())
        cols = list(dataframe.columns)
        self.tree["columns"] = cols
        for col in cols:
            label = COL_LABELS.get(col, col.replace("_", " ").title())
            self.tree.heading(col, text=label, command=lambda c=col: self.sort_treeview_column(c))
            width = 110 if col in ("date", "activity_type") else 90 if col in ("participant_id", "gender") else 120
            self.tree.column(col, width=width, anchor="center")
        for _, row in dataframe.iterrows():
            values = []
            for c in cols:
                val = row[c]
                if c == "date" and isinstance(val, pd.Timestamp):
                    val = val.strftime("%Y-%m-%d")
                values.append(val)
            self.tree.insert("", "end", values=values)

    def filter_treeview(self):
        if self.df is None:
            return
        query = self.search_val.get().lower().strip()
        if not query:
            self.populate_treeview(self.df)
            return
        mask = self.df.astype(str).apply(
            lambda row: row.str.lower().str.contains(query, na=False).any(), axis=1
        )
        filtered = self.df[mask]
        if filtered.empty:
            self.tree.delete(*self.tree.get_children())
            return
        self.populate_treeview(filtered)

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
        self.populate_stats_dashboard()
        self.load_visualization_images()
        self.populate_summary_report()

    def setup_stats_tab(self):
        self.stats_notebook = ttk.Notebook(self.tab_stats)
        self.stats_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stats_desc = ttk.Frame(self.stats_notebook)
        self.stats_cards = ttk.Frame(self.stats_notebook)
        self.stats_corr = ttk.Frame(self.stats_notebook)
        self.stats_group = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(self.stats_desc, text=" Descriptive Statistics ")
        self.stats_notebook.add(self.stats_cards, text=" Health Benchmarks ")
        self.stats_notebook.add(self.stats_corr, text=" Correlation Analysis ")
        self.stats_notebook.add(self.stats_group, text=" Summaries by Group ")

    def populate_stats_dashboard(self):
        if self.stats is None:
            return
        self.draw_descriptive_stats_table()
        self.draw_benchmark_cards()
        self.draw_correlation_table()
        self.draw_group_summary_tables()

    def draw_descriptive_stats_table(self):
        self._clear(self.stats_desc)
        self._section_header(self.stats_desc, "Descriptive Statistics of Numeric Variables")
        table_frame = tk.Frame(self.stats_desc, bg=self.c_card,
                               highlightbackground=self.c_border, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        rows = []
        col_short = {
            "duration_minutes": "duration",
            "calories_burned": "calories",
            "daily_steps": "steps",
            "avg_heart_rate": "heart_rate",
            "sleep_hours": "sleep",
        }
        stat_labels = {
            "mean": "Mean", "median": "Median", "mode": "Mode",
            "std": "Std Dev", "min": "Minimum", "max": "Maximum",
        }
        for stat_key, stat_label in stat_labels.items():
            row = {"statistic": stat_label}
            for col in NUMERIC_COLS:
                val = self.stats["descriptive"][col][stat_key]
                row[col_short[col]] = f"{val:,.2f}" if isinstance(val, (int, float)) else "N/A"
            rows.append(row)

        desc_df = pd.DataFrame(rows)
        self._treeview_from_df(table_frame, desc_df)

    def draw_benchmark_cards(self):
        self._clear(self.stats_cards)
        self._section_header(self.stats_cards, "Participant Health Threshold Benchmarks")
        cards_container = ttk.Frame(self.stats_cards)
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20)

        pcts = self.stats["percentages"]
        step = self.stats["step_benchmark"]
        card_data = [
            ("High Intensity", f"{pcts['high_intensity_pct']}%",
             f"sessions with HR ≥ {HIGH_INTENSITY_HR} bpm", "#C44E52"),
            ("Low Sleep", f"{pcts['low_sleep_pct']}%",
             f"sessions after < {LOW_SLEEP_HOURS} hrs sleep", "#E2B13C"),
            ("High Calorie Burn", f"{pcts['high_calorie_pct']}%",
             f"sessions burning ≥ {HIGH_CALORIE} kcal", "#55A868"),
            ("Step Benchmark", f"{pcts['steps_benchmark_pct']}%",
             f"sessions at ≥ {STEP_BENCHMARK:,} steps ({step['participant_pct_met']:.0f}% of participants)", "#4C72B0"),
            ("Long Sessions", f"{pcts['long_session_pct']}%",
             f"sessions ≥ {LONG_SESSION_MIN} minutes", "#8172B2"),
        ]

        cards_container.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        cards_container.rowconfigure((0, 1), weight=1, uniform="equal")
        for idx, (title, val, desc, color) in enumerate(card_data):
            card = tk.Frame(cards_container, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            card.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=8, pady=8)
            self._card_hover(card)
            tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), fg=self.c_primary, bg=self.c_card).pack(
                anchor="w", padx=15, pady=(15, 5))
            tk.Label(card, text=val, font=("Segoe UI", 24, "bold"), fg=color, bg=self.c_card).pack(anchor="w", padx=15)
            tk.Label(card, text=desc, font=("Segoe UI", 9), fg="#64748B", bg=self.c_card,
                     wraplength=200, justify="left").pack(anchor="w", padx=15, pady=(5, 15))

    def draw_correlation_table(self):
        self._clear(self.stats_corr)
        self._section_header(self.stats_corr, "Correlation Analysis Between Health Variables")
        table_frame = tk.Frame(self.stats_corr, bg=self.c_card,
                               highlightbackground=self.c_border, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        corr = self.stats["correlation_matrix"]
        rows = [
            ("Workout Duration vs Calories", corr.loc["duration_minutes", "calories_burned"],
             "Positive (+)", "Longer sessions burn more calories."),
            ("Sleep Hours vs Heart Rate", corr.loc["sleep_hours", "avg_heart_rate"],
             "Negative (-)", "Less sleep aligns with higher heart rate during activity."),
            ("Daily Steps vs Calories", corr.loc["daily_steps", "calories_burned"],
             "Positive (+)", "More steps align with higher calorie output."),
        ]
        corr_df = pd.DataFrame(rows, columns=["relationship", "r_val", "expected", "interpretation"])
        corr_df["r_val"] = corr_df["r_val"].map(lambda x: f"{x:.3f}")
        self._treeview_from_df(table_frame, corr_df, left_align=("relationship", "interpretation"))

    def draw_group_summary_tables(self):
        self._clear(self.stats_group)
        sub_notebook = ttk.Notebook(self.stats_group)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tab_act = ttk.Frame(sub_notebook)
        tab_eff = ttk.Frame(sub_notebook)
        tab_gen = ttk.Frame(sub_notebook)
        sub_notebook.add(tab_act, text=" By Avg Calories ")
        sub_notebook.add(tab_eff, text=" By Efficiency ")
        sub_notebook.add(tab_gen, text=" By Gender ")

        self._treeview_from_df(tab_act, self.stats["activity_summary"])
        self._treeview_from_df(tab_eff, self.stats["activity_by_efficiency"])
        self._treeview_from_df(tab_gen, self.stats["gender_summary"])

    def setup_viz_tab(self):
        toolbar = tk.Frame(self.tab_viz, bg=self.c_primary, height=45)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        tk.Label(toolbar, text="Charts:", font=("Segoe UI", 10, "bold"),
                 fg="white", bg=self.c_primary).pack(side=tk.LEFT, padx=15)

        chart_buttons = [
            ("Calories by Activity", "bar_calories_by_activity.png"),
            ("Monthly Trend", "line_monthly_calories.png"),
            ("Activity Share", "pie_activity_distribution.png"),
            ("Sleep Distribution", "histogram_sleep_hours.png"),
            ("Steps vs Calories", "scatter_steps_vs_calories.png"),
        ]
        self.active_chart_file = tk.StringVar(value=chart_buttons[0][1])
        for text, filename in chart_buttons:
            tk.Button(toolbar, text=text, font=("Segoe UI", 9, "bold"), bg=self.c_primary, fg="#94A3B8",
                      activebackground="#0F172A", activeforeground="white", bd=0, cursor="hand2",
                      command=lambda f=filename: self.select_active_chart(f)).pack(side=tk.LEFT, padx=8, fill=tk.Y)

        self.chart_container = tk.Frame(self.tab_viz, bg=self.c_card,
                                        highlightbackground=self.c_border, highlightthickness=1)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.lbl_chart = tk.Label(self.chart_container, bg=self.c_card)
        self.lbl_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.chart_container.bind("<Configure>", lambda *_: self.load_visualization_images())

    def select_active_chart(self, filename):
        self.active_chart_file.set(filename)
        self.load_visualization_images()

    def load_visualization_images(self):
        image_path = os.path.join("charts", self.active_chart_file.get())
        width = max(self.chart_container.winfo_width() - 40, 700)
        height = max(self.chart_container.winfo_height() - 40, 450)
        if os.path.exists(image_path):
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
        self.txt_report.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))

        actions = ttk.Frame(self.tab_report)
        actions.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
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
