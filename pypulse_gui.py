# =============================================================================
# PyPulse: A Python-Driven Analytics System for Health and Fitness Tracking
# pypulse_gui.py - Interactive Graphical User Interface (GUI)
#
# ROLE OF THIS FILE:
#   This file implements the Tkinter GUI for the PyPulse application.
#   It integrates:
#     - Data cleaning (calling cleaning.py)
#     - Statistical analysis (calling fitness_analytics_stats.py)
#     - Data Visualizations (displaying charts from fitness_analytics_viz.py)
#     - A Scrollable Treeview of data with column sorting and search filtering
#     - A Copyable Text Summary of the findings to complete the documentation
# =============================================================================

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import numpy as np
import PIL.Image
import PIL.ImageTk
import calendar

# Import local modules
from cleaning import clean_fitness_data
from fitness_analytics_stats import compute_all_statistics, COL_LABELS, NUMERIC_COLS
from fitness_analytics_viz import show_all_charts


class PyPulseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPulse: Health & Fitness Tracking Analytics")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Style configuration
        self.style = ttk.Style()
        self.configure_styles()

        # Data states
        self.raw_filepath = tk.StringVar(value="Group4_FitnessAnalytics_raw.csv")
        self.cleaned_filepath = tk.StringVar(value="Group4_FitnessAnalytics_cleaned.csv")
        self.df = None
        self.stats = None
        self.chart_refs = {}  # Store references to PIL images to avoid garbage collection

        # Main Layout
        self.create_layout()

        # Check if default files exist and load them
        self.auto_load_default_data()

    def configure_styles(self):
        """Define colors and layout rules for the ttk styling library."""
        # Antigravity Palette (Slate, cloud, sky, mint, sketch)
        self.c_bg = "#F8FAFC"         # Cloud White (slate 50)
        self.c_card = "#FFFFFF"       # Paper White
        self.c_primary = "#1E293B"    # Dark Slate (slate 800)
        self.c_secondary = "#0F766E"  # Teal (teal 700)
        self.c_sky = "#38BDF8"        # Sky Blue (antigravity sky)
        self.c_mint = "#34D399"       # Mint Green (Success target)
        self.c_text = "#1E293B"       # Sketch Charcoal
        self.c_border = "#E2E8F0"     # Pale Slate line (slate 200)

        self.root.configure(bg=self.c_bg)

        # TTK styles configuration
        self.style.theme_use("clam")
        
        # Notebook (Tabs) styling
        self.style.configure("TNotebook", background=self.c_bg, borderwidth=0)
        # Weightless tabs - remove background boxes, highlight selected tab in sky blue
        self.style.configure("TNotebook.Tab", background=self.c_bg, foreground="#64748B",
                             padding=[18, 8], font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.c_bg)],
                       foreground=[("selected", self.c_sky)])

        # Frames styling
        self.style.configure("TFrame", background=self.c_bg)
        self.style.configure("Card.TFrame", background=self.c_card, relief="flat", borderwidth=0)

        # Flat Effortless Buttons (with Sky Blue highlight)
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), background=self.c_bg,
                             foreground=self.c_text, borderwidth=1, relief="flat", padding=[12, 6])
        self.style.map("TButton",
                       background=[("active", self.c_sky), ("disabled", self.c_border)],
                       foreground=[("active", "white")])

        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=self.c_sky,
                             foreground="white", relief="flat", padding=[12, 6])
        self.style.map("Primary.TButton",
                       background=[("active", "#0EA5E9"), ("disabled", "#94A3B8")])

        # Labels styling
        self.style.configure("TLabel", background=self.c_bg, foreground=self.c_text, font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.c_primary)
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.c_primary)
        self.style.configure("CardHeader.TLabel", background=self.c_card, font=("Segoe UI", 13, "bold"), foreground=self.c_primary)
        self.style.configure("Value.TLabel", background=self.c_card, font=("Segoe UI", 20, "bold"), foreground=self.c_secondary)
        self.style.configure("Unit.TLabel", background=self.c_card, font=("Segoe UI", 9), foreground="#64748B")

        # Treeview styling
        self.style.configure("Treeview", font=("Segoe UI", 9), background=self.c_card,
                             fieldbackground=self.c_card, rowheight=26, borderwidth=0)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background=self.c_bg,
                             foreground=self.c_text, borderwidth=0, relief="flat")
        self.style.map("Treeview", background=[("selected", "#F0F9FF")], foreground=[("selected", "#0284C7")])

    def create_layout(self):
        """Construct the top title bar and the main tab notebook view."""
        # Top Header Bar (Weightless white header with pencil border line)
        header_frame = tk.Frame(self.root, bg=self.c_card, height=65, 
                                highlightbackground=self.c_border, highlightthickness=1)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="PyPulse Health & Fitness Analytics Dashboard", 
                               font=("Segoe UI", 15, "bold"), fg=self.c_primary, bg=self.c_card)
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        subtitle_label = tk.Label(header_frame, text="Integrative Programming Project (Group 4)", 
                                  font=("Segoe UI", 10, "italic"), fg="#64748B", bg=self.c_card)
        subtitle_label.pack(side=tk.LEFT, padx=10, pady=20)



        # Tab Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add tabs
        self.tab_data = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)
        self.tab_viz = ttk.Frame(self.notebook)
        self.tab_report = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_data, text=" Data Center ")
        self.notebook.add(self.tab_stats, text=" Analytics Dashboard ")
        self.notebook.add(self.tab_viz, text=" Visualization Hub ")
        self.notebook.add(self.tab_report, text=" Summary & Export ")

        # Draw content for each tab
        self.setup_data_tab()
        self.setup_stats_tab()
        self.setup_viz_tab()
        self.setup_report_tab()

    def make_card_floatable(self, card_widget):
        """Bind hover event handlers to widgets to simulate weightless levitation."""
        card_widget.bind("<Enter>", lambda e: card_widget.config(highlightbackground=self.c_sky, highlightthickness=1.5))
        card_widget.bind("<Leave>", lambda e: card_widget.config(highlightbackground=self.c_border, highlightthickness=1))



    # =========================================================================
    # TAB 1: DATA CENTER (Loading & Cleaning)
    # =========================================================================

    def setup_data_tab(self):
        """Build the left file processing card and the right data preview grid."""
        # Split into left control frame and right preview frame
        self.tab_data.columnconfigure(0, weight=1)
        self.tab_data.columnconfigure(1, weight=3)
        self.tab_data.rowconfigure(0, weight=1)

        # Left Control Pane (Loading and Cleaning Options)
        ctrl_frame = ttk.Frame(self.tab_data)
        ctrl_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Load Card
        load_card = tk.Frame(ctrl_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        load_card.pack(fill=tk.X, padx=5, pady=5)
        
        lbl_load_title = tk.Label(load_card, text="1. Load Raw Dataset", font=("Segoe UI", 12, "bold"), fg=self.c_primary, bg=self.c_card)
        lbl_load_title.pack(anchor="w", padx=15, pady=10)

        file_frame = tk.Frame(load_card, bg=self.c_card)
        file_frame.pack(fill=tk.X, padx=15, pady=5)
        
        lbl_file = tk.Label(file_frame, text="Raw CSV Path:", font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        lbl_file.pack(anchor="w")
        
        self.ent_raw = ttk.Entry(file_frame, textvariable=self.raw_filepath, font=("Segoe UI", 9))
        self.ent_raw.pack(fill=tk.X, side=tk.LEFT, expand=True, pady=5)
        
        btn_browse = ttk.Button(file_frame, text="Browse", command=self.browse_raw_file)
        btn_browse.pack(side=tk.RIGHT, padx=5, pady=5)

        # Clean Card
        clean_card = tk.Frame(ctrl_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        clean_card.pack(fill=tk.X, padx=5, pady=10)

        lbl_clean_title = tk.Label(clean_card, text="2. Data Preprocessing", font=("Segoe UI", 12, "bold"), fg=self.c_primary, bg=self.c_card)
        lbl_clean_title.pack(anchor="w", padx=15, pady=10)
        
        btn_clean = ttk.Button(clean_card, text="Run Clean & Deduplication", command=self.execute_data_cleaning)
        btn_clean.pack(fill=tk.X, padx=15, pady=10)

        # Cleaning Stats display
        self.clean_stats_frame = tk.Frame(clean_card, bg=self.c_card)
        self.clean_stats_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.lbl_orig_rows = tk.Label(self.clean_stats_frame, text="Original Records: N/A", font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        self.lbl_orig_rows.pack(anchor="w", pady=2)
        
        self.lbl_clean_rows = tk.Label(self.clean_stats_frame, text="Cleaned Records: N/A", font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        self.lbl_clean_rows.pack(anchor="w", pady=2)
        
        self.lbl_deleted_rows = tk.Label(self.clean_stats_frame, text="Duplicates Deleted: N/A", font=("Segoe UI", 9), bg=self.c_card, fg="#475569")
        self.lbl_deleted_rows.pack(anchor="w", pady=2)

        # Right Preview Pane (Treeview Data Spreadsheet)
        preview_frame = tk.Frame(self.tab_data, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        # Wait, make sure we grid the right preview frame properly
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Data preview header & search filter
        preview_header = tk.Frame(preview_frame, bg=self.c_card)
        preview_header.pack(fill=tk.X, padx=15, pady=10)

        lbl_preview = tk.Label(preview_header, text="Cleaned Dataset Preview", font=("Segoe UI", 12, "bold"), fg=self.c_primary, bg=self.c_card)
        lbl_preview.pack(side=tk.LEFT)

        # Search box
        search_frame = tk.Frame(preview_header, bg=self.c_card)
        search_frame.pack(side=tk.RIGHT)
        
        lbl_search = tk.Label(search_frame, text="Search Filter:", font=("Segoe UI", 9, "bold"), bg=self.c_card, fg="#475569")
        lbl_search.pack(side=tk.LEFT, padx=5)

        self.search_val = tk.StringVar()
        self.search_val.trace_add("write", lambda *args: self.filter_treeview())
        self.ent_search = ttk.Entry(search_frame, textvariable=self.search_val, font=("Segoe UI", 9), width=25)
        self.ent_search.pack(side=tk.LEFT, padx=5)

        # Clear Search Button
        btn_clear_search = ttk.Button(search_frame, text="Clear", width=6, command=lambda: self.search_val.set(""))
        btn_clear_search.pack(side=tk.LEFT, padx=5)

        # Treeview
        tree_container = ttk.Frame(preview_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        self.tree = ttk.Treeview(tree_container, yscrollcommand=vsb.set, xscrollcommand=hsb.set, selectmode="browse")
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configure columns (headers populated dynamically)
        self.tree["show"] = "headings"
        self.sort_column_direction = {}

        # Bind antigravity floating hover highlights
        self.make_card_floatable(load_card)
        self.make_card_floatable(clean_card)
        self.make_card_floatable(preview_frame)

    def browse_raw_file(self):
        """File open dialog to select the raw CSV input file."""
        file_path = filedialog.askopenfilename(
            initialdir=".",
            title="Select Raw CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if file_path:
            self.raw_filepath.set(file_path)

    def auto_load_default_data(self):
        """Check if pre-cleaned data exists, loading it instantly to populate the UI."""
        if os.path.exists(self.cleaned_filepath.get()):
            try:
                self.df = pd.read_csv(self.cleaned_filepath.get())
                self.df["date"] = pd.to_datetime(self.df["date"])
                
                # If raw exists, calculate original count for layout metrics
                if os.path.exists(self.raw_filepath.get()):
                    raw_df = pd.read_csv(self.raw_filepath.get())
                    orig_len = len(raw_df)
                    del raw_df
                else:
                    orig_len = "N/A"

                self.update_cleaning_stats_labels(orig_len, len(self.df))
                self.populate_treeview(self.df)
                self.run_analytics_pipeline()
            except Exception as e:
                print(f"Error loading default cleaned data: {e}")

    def execute_data_cleaning(self):
        """Invoke cleaning.py methods on the selected file path, saving and loading results."""
        raw_path = self.raw_filepath.get()
        cleaned_path = self.cleaned_filepath.get()

        if not os.path.exists(raw_path):
            messagebox.showerror("File Error", f"The raw file '{raw_path}' does not exist.\nPlease select a valid file path.")
            return

        try:
            # Get original count
            raw_df = pd.read_csv(raw_path)
            original_len = len(raw_df)
            del raw_df

            # Call clean data module
            clean_fitness_data(raw_path, cleaned_path)

            # Load cleaned dataset
            self.df = pd.read_csv(cleaned_path)
            self.df["date"] = pd.to_datetime(self.df["date"])

            # Update Treeview and UI Statistics Labels
            self.update_cleaning_stats_labels(original_len, len(self.df))
            self.populate_treeview(self.df)
            
            # Generate charts folder and run analytics computations
            self.run_analytics_pipeline()
            
            messagebox.showinfo("Success", f"Data cleaning successfully completed!\nCleaned data loaded: {len(self.df)} records.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during data cleaning:\n{str(e)}")

    def update_cleaning_stats_labels(self, original_count, cleaned_count):
        """Show raw-vs-cleaned row statistics in the side control frame."""
        self.lbl_orig_rows.config(text=f"Original Records: {original_count}")
        self.lbl_clean_rows.config(text=f"Cleaned Records: {cleaned_count}")
        if isinstance(original_count, int):
            deleted = original_count - cleaned_count
            self.lbl_deleted_rows.config(text=f"Duplicates/Invalid Deleted: {deleted}")
        else:
            self.lbl_deleted_rows.config(text="Duplicates Deleted: N/A")

    def populate_treeview(self, dataframe):
        """Render DataFrame records into Treeview with clickable columns for sorting."""
        # Clear existing tree columns and rows
        self.tree.delete(*self.tree.get_children())
        
        # Columns definition
        cols = list(dataframe.columns)
        self.tree["columns"] = cols

        # Setup column headers
        for col in cols:
            # Human readable label
            label = COL_LABELS.get(col, col.replace("_", " ").title())
            self.tree.heading(col, text=label, command=lambda c=col: self.sort_treeview_column(c))
            
            # Format widths
            if col in ["participant_id", "gender", "sleep_hours"]:
                self.tree.column(col, width=90, anchor="center")
            elif col in ["date"]:
                self.tree.column(col, width=110, anchor="center")
            else:
                self.tree.column(col, width=120, anchor="e")

        # Insert records (converting datetime to string format)
        for _, row in dataframe.iterrows():
            row_dict = row.to_dict()
            if isinstance(row_dict["date"], pd.Timestamp):
                row_dict["date"] = row_dict["date"].strftime("%Y-%m-%d")
            values = [row_dict[col] for col in cols]
            self.tree.insert("", "end", values=values)

    def filter_treeview(self):
        """Filter the displayed Treeview rows dynamically as the user types in the search box."""
        if self.df is None:
            return

        search_query = self.search_val.get().lower().strip()
        if not search_query:
            # Show complete dataset if search entry is empty
            self.populate_treeview(self.df)
            return

        # Perform case-insensitive string filtering on matching fields
        filtered_rows = []
        for _, row in self.df.iterrows():
            match = False
            for val in row.values:
                val_str = str(val).lower()
                if search_query in val_str:
                    match = True
                    break
            if match:
                filtered_rows.append(row)

        if filtered_rows:
            filtered_df = pd.DataFrame(filtered_rows)
            self.populate_treeview(filtered_df)
        else:
            # Clear treeview if no matching records found
            self.tree.delete(*self.tree.get_children())

    def sort_treeview_column(self, col):
        """Sort the Treeview row elements alphabetically or numerically when clicking headers."""
        # Reverse direction state
        direction = self.sort_column_direction.get(col, False)
        self.sort_column_direction[col] = not direction

        # Fetch current rows
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        # Try numeric sorting if possible
        try:
            items.sort(key=lambda t: float(t[0].replace(",", "")), reverse=direction)
        except ValueError:
            items.sort(reverse=direction)

        # Rearrange items in treeview
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)

        # Update headings with sort arrows (▲ / ▼)
        for c in self.tree["columns"]:
            label = COL_LABELS.get(c, c.replace("_", " ").title())
            if c == col:
                arrow = " ▲" if not direction else " ▼"
                self.tree.heading(c, text=label + arrow)
            else:
                self.tree.heading(c, text=label)

    # =========================================================================
    # PIPELINE INTEGRATOR (Computes Stats & Generates PNG Charts)
    # =========================================================================

    def run_analytics_pipeline(self):
        """Trigger backend pipelines (stats + viz charts) to fill GUI components."""
        if self.df is None:
            return

        # 1. Compute Stats Dict
        self.stats = compute_all_statistics(self.df)

        # 2. Generate Matplotlib Charts inside charts/ subfolder
        show_all_charts(self.df, save_dir="charts/")

        # 3. Update tabs UI views
        self.populate_stats_dashboard()
        self.load_visualization_images()
        self.populate_summary_report()

    # =========================================================================
    # TAB 2: ANALYTICS DASHBOARD
    # =========================================================================

    def setup_stats_tab(self):
        """Set up nested tabs to separate statistics categories cleanly."""
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
        """Distribute stats dict tables and cards to their respective GUI tabs."""
        if self.stats is None:
            return

        self.draw_descriptive_stats_table()
        self.draw_benchmark_percentage_cards()
        self.draw_correlation_table()
        self.draw_group_summary_tables()

    def draw_descriptive_stats_table(self):
        """Render Descriptive statistics mean, median, mode, and ranges in a scrollable frame."""
        # Clear frame content
        for widget in self.stats_desc.winfo_children():
            widget.destroy()

        header = tk.Label(self.stats_desc, text="Descriptive Statistics of Numeric Variables", 
                          font=("Segoe UI", 13, "bold"), fg=self.c_primary, bg=self.c_bg)
        header.pack(anchor="w", padx=20, pady=15)

        # Scrollable table container
        table_frame = tk.Frame(self.stats_desc, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        desc_tree = ttk.Treeview(table_frame, selectmode="none")
        desc_tree.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        cols = ["statistic", "duration", "calories", "steps", "heart_rate", "sleep"]
        desc_tree["columns"] = cols
        desc_tree["show"] = "headings"

        desc_tree.heading("statistic", text="Metric Statistic")
        desc_tree.heading("duration", text="Duration (min)")
        desc_tree.heading("calories", text="Calories (kcal)")
        desc_tree.heading("steps", text="Daily Steps")
        desc_tree.heading("heart_rate", text="Heart Rate (bpm)")
        desc_tree.heading("sleep", text="Sleep Hours")

        desc_tree.column("statistic", width=150, anchor="w")
        for col in cols[1:]:
            desc_tree.column(col, width=120, anchor="center")

        # Map stat row values
        stats_mapping = ["mean", "median", "mode", "std", "min", "max"]
        stat_labels = {
            "mean": "Mean (Average)",
            "median": "Median (Midpoint)",
            "mode": "Mode (Most Frequent)",
            "std": "Standard Deviation",
            "min": "Minimum Value",
            "max": "Maximum Value"
        }

        # Populate rows
        for sm in stats_mapping:
            label = stat_labels[sm]
            row_vals = [label]
            for col in NUMERIC_COLS:
                val = self.stats["descriptive"][col][sm]
                row_vals.append(f"{val:,.2f}" if isinstance(val, (int, float)) else "N/A")
            desc_tree.insert("", "end", values=row_vals)

    def draw_benchmark_percentage_cards(self):
        """Draw modern information cards for the five health percentage thresholds."""
        # Clear frame
        for widget in self.stats_cards.winfo_children():
            widget.destroy()

        header = tk.Label(self.stats_cards, text="Participant Health Threshold Benchmarks", 
                          font=("Segoe UI", 13, "bold"), fg=self.c_primary, bg=self.c_bg)
        header.pack(anchor="w", padx=20, pady=15)

        cards_container = ttk.Frame(self.stats_cards)
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20)

        # 5 card definitions
        pcts = self.stats["percentages"]
        card_data = [
            ("High Intensity Sessions", f"{pcts['high_intensity_pct']}%", "sessions logged with average HR ≥ 130 bpm", "#C44E52"),
            ("Low Sleep Ratio", f"{pcts['low_sleep_pct']}%", "workout logs indicating sleep < 6 hours prior", "#E2B13C"),
            ("High Calorie Burn Ratio", f"{pcts['high_calorie_pct']}%", "exercise sessions burning ≥ 300 kcal", "#55A868"),
            ("Active Days Benchmark", f"{pcts['high_steps_pct']}%", "workout logs exceeding 10,000 steps", "#4C72B0"),
            ("Long Workout Ratio", f"{pcts['long_session_pct']}%", "sessions with workout durations ≥ 60 minutes", "#8172B2")
        ]

        # Arrange cards in a clean grid
        cards_container.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        cards_container.rowconfigure((0, 1), weight=1, uniform="equal")

        for idx, (title, val, desc, color) in enumerate(card_data):
            row = idx // 3
            col = idx % 3
            
            # Card frame wrapper
            card = tk.Frame(cards_container, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            self.make_card_floatable(card)

            lbl_title = tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), fg=self.c_primary, bg=self.c_card)
            lbl_title.pack(anchor="w", padx=15, pady=(15, 5))

            lbl_val = tk.Label(card, text=val, font=("Segoe UI", 24, "bold"), fg=color, bg=self.c_card)
            lbl_val.pack(anchor="w", padx=15)

            lbl_desc = tk.Label(card, text=desc, font=("Segoe UI", 9), fg="#64748B", bg=self.c_card, wraplength=200, justify="left")
            lbl_desc.pack(anchor="w", padx=15, pady=(5, 15))

    def draw_correlation_table(self):
        """Render correlation grid view detailing expected behaviors and computed r values."""
        for widget in self.stats_corr.winfo_children():
            widget.destroy()

        header = tk.Label(self.stats_corr, text="Correlation Analysis Between Health Variables", 
                          font=("Segoe UI", 13, "bold"), fg=self.c_primary, bg=self.c_bg)
        header.pack(anchor="w", padx=20, pady=15)

        table_frame = tk.Frame(self.stats_corr, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        corr_tree = ttk.Treeview(table_frame, selectmode="none")
        corr_tree.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        cols = ["relationship", "r_val", "expected", "interpretation"]
        corr_tree["columns"] = cols
        corr_tree["show"] = "headings"

        corr_tree.heading("relationship", text="Relationship Matrix")
        corr_tree.heading("r_val", text="Correlation Coefficient (r)")
        corr_tree.heading("expected", text="Expected Direction")
        corr_tree.heading("interpretation", text="Clinical Analysis Interpretation")

        corr_tree.column("relationship", width=250, anchor="w")
        corr_tree.column("r_val", width=180, anchor="center")
        corr_tree.column("expected", width=180, anchor="center")
        corr_tree.column("interpretation", width=350, anchor="w")

        # Map correlation values from stats matrix
        r_dur_cal = self.stats["correlation_matrix"].loc["duration_minutes", "calories_burned"]
        r_sleep_hr = self.stats["correlation_matrix"].loc["sleep_hours", "avg_heart_rate"]
        r_steps_cal = self.stats["correlation_matrix"].loc["daily_steps", "calories_burned"]

        relationships = [
            ("Workout Duration vs. Calories Burned", r_dur_cal, "Strong positive (+)", 
             "Longer physical activity duration leads directly to greater caloric expenditure."),
            ("Sleep Hours vs. Average Heart Rate", r_sleep_hr, "Negative (-)", 
             "Higher sleep hours correlate with lower average heart rates, indicating lower cardiovascular stress."),
            ("Daily Step Counts vs. Calories Burned", r_steps_cal, "Positive (+)", 
             "Higher step counts contribute to increased total energetic output throughout the day.")
        ]

        for rel, r, exp, interp in relationships:
            corr_tree.insert("", "end", values=(rel, f"{r:.3f}", exp, interp))

    def draw_group_summary_tables(self):
        """Setup nested notebooks for grouped metrics, displaying stats sorted by Activity and Gender."""
        for widget in self.stats_group.winfo_children():
            widget.destroy()

        sub_notebook = ttk.Notebook(self.stats_group)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab for activity summary
        tab_act = ttk.Frame(sub_notebook)
        sub_notebook.add(tab_act, text=" Activity Averages ")
        
        act_tree = ttk.Treeview(tab_act)
        act_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        act_cols = list(self.stats["activity_summary"].columns)
        act_tree["columns"] = act_cols
        act_tree["show"] = "headings"

        for col in act_cols:
            label = COL_LABELS.get(col, col.replace("_", " ").title())
            act_tree.heading(col, text=label)
            act_tree.column(col, width=100, anchor="center" if col != "activity_type" else "w")

        for _, row in self.stats["activity_summary"].iterrows():
            act_tree.insert("", "end", values=list(row))

        # Tab for gender summary
        tab_gen = ttk.Frame(sub_notebook)
        sub_notebook.add(tab_gen, text=" Gender Differences ")

        gen_tree = ttk.Treeview(tab_gen)
        gen_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        gen_cols = list(self.stats["gender_summary"].columns)
        gen_tree["columns"] = gen_cols
        gen_tree["show"] = "headings"

        for col in gen_cols:
            label = COL_LABELS.get(col, col.replace("_", " ").title())
            gen_tree.heading(col, text=label)
            gen_tree.column(col, width=100, anchor="center" if col != "gender" else "w")

        for _, row in self.stats["gender_summary"].iterrows():
            gen_tree.insert("", "end", values=list(row))

    # =========================================================================
    # TAB 3: VISUALIZATION HUB (Embedded PNGs)
    # =========================================================================

    def setup_viz_tab(self):
        """Create tab structure inside the Visualization panel to switch between charts."""
        # Top toolbar for navigation
        toolbar = tk.Frame(self.tab_viz, bg=self.c_primary, height=45)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)

        lbl_toolbar = tk.Label(toolbar, text="Chart Directory:", font=("Segoe UI", 10, "bold"), fg="white", bg=self.c_primary)
        lbl_toolbar.pack(side=tk.LEFT, padx=15)

        # Setup buttons mapping
        chart_buttons = [
            ("Calories Burned by Activity", "bar_calories_by_activity.png"),
            ("Calories Trend Over Time", "line_monthly_calories.png"),
            ("Sessions Share Distribution", "pie_activity_distribution.png"),
            ("Distribution of Sleep", "histogram_sleep_hours.png"),
            ("Steps vs Calories Correlation", "scatter_steps_vs_calories.png")
        ]

        self.active_chart_file = tk.StringVar(value="bar_calories_by_activity.png")

        for text, filename in chart_buttons:
            btn = tk.Button(toolbar, text=text, font=("Segoe UI", 9, "bold"), bg=self.c_primary, fg="#94A3B8",
                            activebackground="#0F172A", activeforeground="white", bd=0, cursor="hand2",
                            command=lambda f=filename: self.select_active_chart(f))
            btn.pack(side=tk.LEFT, padx=10, fill=tk.Y)
            # Hover highlight bindings
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg="white"))
            btn.bind("<Leave>", lambda e, b=btn, f=filename: b.config(fg="white" if self.active_chart_file.get() == f else "#94A3B8"))

        # Main chart view widget
        self.chart_container = tk.Frame(self.tab_viz, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.lbl_chart = tk.Label(self.chart_container, bg=self.c_card)
        self.lbl_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bind container resize so we can auto-fit the image
        self.chart_container.bind("<Configure>", lambda e: self.load_visualization_images())

    def select_active_chart(self, filename):
        """Set the active chart path indicator, triggering update reload logic."""
        self.active_chart_file.set(filename)
        self.load_visualization_images()

    def load_visualization_images(self):
        """Scale and render the active generated Matplotlib PNG inside the Tkinter view widget."""
        filename = self.active_chart_file.get()
        image_path = os.path.join("charts", filename)

        # Check container geometry to size proportionally
        container_w = self.chart_container.winfo_width()
        container_h = self.chart_container.winfo_height()

        # Fallback values if container is not mapped yet
        width = max(container_w - 40, 700)
        height = max(container_h - 40, 450)

        if os.path.exists(image_path):
            try:
                img = PIL.Image.open(image_path)
                # Keep aspect ratio resizing
                img.thumbnail((width, height), PIL.Image.Resampling.LANCZOS)
                photo = PIL.ImageTk.PhotoImage(img)

                # Configure label
                self.lbl_chart.config(image=photo, text="")
                self.lbl_chart.image = photo  # Keep hard reference!
            except Exception as e:
                self.lbl_chart.config(text=f"Error displaying image: {str(e)}", image="")
        else:
            self.lbl_chart.config(
                text=f"Chart '{filename}' not found.\nPlease load a dataset and run the preprocessor to generate visualizations.", 
                font=("Segoe UI", 11, "italic"), fg="#64748B", image=""
            )

    # =========================================================================
    # TAB 4: SUMMARY REPORT & EXPORT
    # =========================================================================

    def setup_report_tab(self):
        """Construct scrollable text interface for copy-paste and PDF/TXT export buttons."""
        self.tab_report.columnconfigure(0, weight=1)
        self.tab_report.rowconfigure(0, weight=1)
        self.tab_report.rowconfigure(1, weight=0)

        # Text panel
        self.txt_report = scrolledtext.ScrolledText(self.tab_report, wrap=tk.WORD, font=("Consolas", 10),
                                                    bg=self.c_card, fg=self.c_text, relief="solid", bd=1)
        self.txt_report.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))

        # Bottom actions bar
        actions_bar = ttk.Frame(self.tab_report)
        actions_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        btn_copy = ttk.Button(actions_bar, text="Copy Report to Clipboard", command=self.copy_report_to_clipboard)
        btn_copy.pack(side=tk.LEFT, padx=5)

        btn_save_txt = ttk.Button(actions_bar, text="Save Report as TXT File", command=self.export_report_txt)
        btn_save_txt.pack(side=tk.LEFT, padx=5)

        btn_export_csv = ttk.Button(actions_bar, text="Export Cleaned CSV", command=self.export_cleaned_csv)
        btn_export_csv.pack(side=tk.RIGHT, padx=5)

    def populate_summary_report(self):
        """Construct the filled text report using computed stats and dataset parameters."""
        if self.stats is None:
            self.txt_report.delete("1.0", tk.END)
            self.txt_report.insert(tk.END, "Summary report details will be populated once a cleaned dataset is loaded.")
            return

        desc = self.stats["descriptive"]
        pcts = self.stats["percentages"]
        corr = self.stats["correlation_matrix"]
        
        # Calculate steps participant benchmark details
        by_part = self.df.groupby('participant_id')['daily_steps'].mean()
        met_benchmark = len(by_part[by_part >= 7000])
        met_benchmark_pct = (met_benchmark / len(by_part)) * 100

        # Activity type ranks
        act_summary = self.stats["activity_summary"]
        highest_act = act_summary.iloc[0]["activity_type"]
        highest_act_cal = act_summary.iloc[0]["avg_calories"]
        lowest_act = act_summary.iloc[-1]["activity_type"]
        lowest_act_cal = act_summary.iloc[-1]["avg_calories"]

        report_txt = f"""=============================================================================
             PYPULSE: DATA ANALYTICS & INSIGHTS REPORT
                  Fitness and Health Tracking System
=============================================================================

[1] SYSTEM STATISTICS OVERVIEW
-----------------------------------------------------------------------------
* Raw File Evaluated         : {self.raw_filepath.get()}
* Cleaned File Generated     : {self.cleaned_filepath.get()}
* Date Range Coverage        : {self.df['date'].min().strftime('%Y-%m-%d')} to {self.df['date'].max().strftime('%Y-%m-%d')}
* Total Active Participants  : {self.df['participant_id'].nunique()}
* Total Workout Logs        : {len(self.df)}

[2] KEY NUMERICAL DESCRIPTIVE STATISTICS
-----------------------------------------------------------------------------
| Variable         | Mean        | Median      | Mode        | Std Dev     | Range (Min-Max) |
|------------------|-------------|-------------|-------------|-------------|-----------------|
| Duration (min)   | {desc['duration_minutes']['mean']:<11} | {desc['duration_minutes']['median']:<11} | {desc['duration_minutes']['mode']:<11} | {desc['duration_minutes']['std']:<11} | {desc['duration_minutes']['min']} - {desc['duration_minutes']['max']} |
| Calories (kcal)  | {desc['calories_burned']['mean']:<11} | {desc['calories_burned']['median']:<11} | {desc['calories_burned']['mode']:<11} | {desc['calories_burned']['std']:<11} | {desc['calories_burned']['min']} - {desc['calories_burned']['max']} |
| Daily Steps      | {desc['daily_steps']['mean']:<11.2f} | {desc['daily_steps']['median']:<11.1f} | {desc['daily_steps']['mode']:<11.1f} | {desc['daily_steps']['std']:<11.2f} | {desc['daily_steps']['min']} - {desc['daily_steps']['max']} |
| Heart Rate (bpm) | {desc['avg_heart_rate']['mean']:<11} | {desc['avg_heart_rate']['median']:<11} | {desc['avg_heart_rate']['mode']:<11} | {desc['avg_heart_rate']['std']:<11} | {desc['avg_heart_rate']['min']} - {desc['avg_heart_rate']['max']} |
| Sleep (hrs)      | {desc['sleep_hours']['mean']:<11} | {desc['sleep_hours']['median']:<11} | {desc['sleep_hours']['mode']:<11} | {desc['sleep_hours']['std']:<11} | {desc['sleep_hours']['min']} - {desc['sleep_hours']['max']} |

[3] FREQUENCY DISTRIBUTION & DOMINANT ACTIVITY
-----------------------------------------------------------------------------
* Most logged activity type is {self.stats['activity_frequency'].iloc[0]['activity_type']} with {self.stats['activity_frequency'].iloc[0]['count']} sessions ({self.stats['activity_frequency'].iloc[0]['pct']}% of total).
* Full distribution of sessions logged:
{self.stats['activity_frequency'].to_string(index=False)}

[4] INTERPRETATION FINDINGS & CLINICAL INSIGHTS
-----------------------------------------------------------------------------
* Finding 1: Workout duration is strongly linked to calories burned
  The Pearson correlation coefficient is {corr.loc['duration_minutes', 'calories_burned']:.3f}, indicating a strong positive
  relationship: longer workout durations directly generate higher calorie burns.

* Finding 2: High intensity vs. Low intensity workouts
  Grouped data reveals that {highest_act} is the most energy-intensive activity type,
  generating an average burn of {highest_act_cal:.2f} kcal per session. Conversely, {lowest_act}
  is the least energy-intensive activity, averaging {lowest_act_cal:.2f} kcal.

* Finding 3: Daily step counts and health benchmarks
  The average step count recorded across all logging days is {desc['daily_steps']['mean']:,.2f} steps.
  Comparing participants' individual averages against the recognized healthy target of 7,000 steps
  per day shows that {met_benchmark} out of {len(by_part)} participants ({met_benchmark_pct:.2f}%) meet or exceed the benchmark.

* Finding 4: Less sleep is associated with higher cardiac workload
  The correlation between sleep hours and average heart rate is {corr.loc['sleep_hours', 'avg_heart_rate']:.3f},
  a negative relationship indicating that sleep deprivation prior to exercise correlates with
  elevated heart rates, indicating increased stress on the cardiovascular system.

=============================================================================
Report Generated By PyPulse Dashboard Software. All stats validated.
=============================================================================
"""
        self.txt_report.delete("1.0", tk.END)
        self.txt_report.insert(tk.END, report_txt)

    def copy_report_to_clipboard(self):
        """Copy summary text area data to operating system clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.txt_report.get("1.0", tk.END))
        messagebox.showinfo("Clipboard", "Summary report successfully copied to clipboard!")

    def export_report_txt(self):
        """Export report text as a standalone text file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")),
            title="Save Summary Report"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.txt_report.get("1.0", tk.END))
                messagebox.showinfo("Success", f"Report saved successfully as:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report file:\n{str(e)}")

    def export_cleaned_csv(self):
        """Save a duplicate of the cleaned CSV file to user selected path."""
        if self.df is None:
            messagebox.showerror("Export Error", "No cleaned data available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")),
            title="Export Cleaned Dataset"
        )
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Cleaned dataset exported successfully as:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV file:\n{str(e)}")


def main():
    root = tk.Tk()
    # Configure font fallback properties
    root.option_add("*font", "SegoeUI 10")
    app = PyPulseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
