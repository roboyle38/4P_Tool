"""
main_window.py

Qt main window for the 4P Assay Tool.

Responsibilities:
- Owns the MainWindow class.
- Knows about:
    - Buttons
    - Menu actions
    - High-level layout (plot + parameter table + data tables)
- Delegates to:
    - analysis.run_analysis for all calculations
    - plotter.plot_full_calibration for plotting
    - reporter helpers for table formatting/population
"""

# ---------------------------------------------------------------------------
# Import path patchwork (so imports work when running from different locations)
# ---------------------------------------------------------------------------
import os
import sys

# 1) Find the folder that *this* file (main_window.py) is in
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 2) Go one level up: that’s your 4P_Tool project root
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
# 3) Tell Python to also look there for imports
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Third-party and internal imports
# ---------------------------------------------------------------------------
from analysis import run_analysis
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFileDialog,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QPushButton,
    QHeaderView,
    QSplitter,
    QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from plotter import plot_full_calibration
from model_4pl import four_pl
import numpy as np
from helpers.helper_fnx import cv_calc
from reporter import (
    unknown_table,
    calibration_table,
    fill_table_widget,
    params_table_builder,
    add_unknown_status_column,
)
from exporter import export_csv
from plotter import plot_full_calibration, plot_residuals, plot_residuals_vs_fitted
"""
PySide6 is the Python binding for the Qt GUI framework.
It provides standard widgets and layout tools such as:

- QMainWindow (main application window)
- QPushButton (button)
- QLabel (text label)
- QTableWidget (table)
- QVBoxLayout / QHBoxLayout (layout managers)

MainWindow below subclasses QMainWindow to define the app UI.
"""


class MainWindow(QMainWindow):
    """
    Main application window for the 4P Assay Tool.

    Coordinates:
    - Loading a CSV via File menu / Load CSV button
    - Running analysis on the data
    - Updating the plot, parameter table, unknown table, and calibration table
    """
    def __init__(self):
            """Initialize the main window UI and connect signals."""
            super().__init__()

            self.setWindowTitle("4P Assay Tool")
            self.resize(900, 600)

            self.central = QWidget()
            self.layout = QVBoxLayout()
            self.central.setLayout(self.layout)
            self.setCentralWidget(self.central)

            self.status_label = QLabel("No file loaded.")
            self.layout.addWidget(self.status_label)
            self.statusBar().showMessage("Ready")

            self.button_row = QHBoxLayout()
            self.load_csv = QPushButton("Load CSV")
            self.clear_button = QPushButton("Clear Plot")
            self.button_row.addWidget(self.load_csv)
            self.button_row.addWidget(self.clear_button)
            self.layout.addLayout(self.button_row)

            self.load_csv.clicked.connect(self.open_csv)
            self.clear_button.clicked.connect(self.on_clear_clicked)

            self._create_menus()

            self.tabs = QTabWidget()

            self.tab1 = QWidget()
            self.tab1_layout = QHBoxLayout()
            self.tab1.setLayout(self.tab1_layout)
            self.figure = Figure()
            self.canvas = FigureCanvas(self.figure)
            self.tab1_layout.addWidget(self.canvas)
            self.params_table = QTableWidget()
            self.params_table.setColumnCount(2)
            self.params_table.setHorizontalHeaderLabels(["Parameter", "Value"])
            self.tab1_layout.addWidget(self.params_table)
            self.tabs.addTab(self.tab1, "Calibration Curve")

            self.tab2 = QWidget()
            self.tab2_layout = QVBoxLayout()
            self.tab2.setLayout(self.tab2_layout)
            self.residual_figure = Figure()
            self.residual_canvas = FigureCanvas(self.residual_figure)
            self.tab2_layout.addWidget(self.residual_canvas)
            self.tabs.addTab(self.tab2, "Residual Plot")

            #Add 3rd tab for fitted v residuals
            # referred to as residual_2

            self.tab3 = QWidget()
            self.tab3_layout = QVBoxLayout()
            self.tab3.setLayout(self.tab3_layout)
            self.residual_vs_fitted_figure = Figure()
            self.residual_vs_fitted_canvas = FigureCanvas(self.residual_vs_fitted_figure)
            self.tab3_layout.addWidget(self.residual_vs_fitted_canvas)
            self.tabs.addTab(self.tab3, "Residual vs Fitted Plot")

            self.layout.addWidget(self.tabs)

            self.unknown_table = QTableWidget()
            header = self.unknown_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            self.unknown_table.verticalHeader().setDefaultSectionSize(16)
            font = self.unknown_table.font()
            font.setPointSize(9)
            self.unknown_table.setFont(font)
            self.unknown_table.setColumnCount(6)
            self.unknown_table.setHorizontalHeaderLabels(
                ["Sample ID", "N Reps", "Mean", "CV%", "Min", "Max"]
            )
            self.layout.addWidget(self.unknown_table)

            self.calibration_data_table = QTableWidget()
            header = self.calibration_data_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            self.calibration_data_table.verticalHeader().setDefaultSectionSize(16)
            font = self.calibration_data_table.font()
            font.setPointSize(9)
            self.calibration_data_table.setFont(font)
            self.layout.addWidget(self.calibration_data_table)

            self.layout.setStretchFactor(self.tabs, 3)
            self.layout.setStretchFactor(self.unknown_table, 1)
            self.layout.setStretchFactor(self.calibration_data_table, 1)

    # -----------------------------------------------------------------------
    # UI handlers
    # -----------------------------------------------------------------------
    def on_clear_clicked(self):
        """Clear the plot area (Figure + Canvas)."""
        self.figure.clear()
        self.canvas.draw()
        self.statusBar().showMessage("Plot cleared", 3000)

    def _create_menus(self):
        """Create the menubar and its actions."""
        menubar = self.menuBar()

        # ---- File menu ----
        file_menu = menubar.addMenu("File")

        # Open CSV
        open_action = QAction("Open CSV", self)
        open_action.triggered.connect(self.open_csv)
        file_menu.addAction(open_action)

        # Export CSV
        export_action = QAction("Export CSV", self)
        export_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_action)

        # Quit
        quit_action = QAction("Quit", self)
        quit_action.setMenuRole(QAction.NoRole)  # tell macOS not to move it
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    # -----------------------------------------------------------------------
    # Core workflow: open CSV -> run analysis -> update UI
    # -----------------------------------------------------------------------
    def open_csv(self):
        """
        Ask the user for a CSV file, run the analysis pipeline,
        then update the plot and all tables.
        """
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV file",
            "",
            "CSV Files (*.csv)",
        )

        if filepath:
            # Update status labels
            print("User opened:", filepath)
            self.status_label.setText("Loaded: " + filepath)
            self.status_label.setText(f"Loaded: {os.path.basename(filepath)}")
            self.statusBar().showMessage("Running analysis...", 1000)
            self.statusBar().showMessage("Analysis complete.", 50000)

            # ---------------------------------------------------------------
            # 1) Run analysis pipeline on this file
            # ---------------------------------------------------------------
            (
                x_axis,
                y_axis,
                A, B, C, D,
                unk_rep_x, unk_rep_y,
                unk_mean_x, unk_mean_y,
                results,
                calibration_groups,
                calibration_stats,
                uloq,
                lloq,
                r2,
                sse,
                residual_sd,
                x_all_reps,
                y_all_reps
            ) = run_analysis(filepath)


            # ---------------------------------------------------------------
            # 2) Update plot (4PL curve + unknowns)
            # ---------------------------------------------------------------
            plot_full_calibration(
                self.figure,
                self.canvas,
                x_axis,
                y_axis,
                A, B, C, D,
                unk_rep_x,
                unk_rep_y,
                unk_mean_x,
                unk_mean_y,
                lloq,
                uloq
            )


            plot_residuals(
                self.residual_figure,
                self.residual_canvas,
                x_all_reps,
                y_all_reps,
                A, B, C, D,
            )

            plot_residuals_vs_fitted(
                self.residual_vs_fitted_figure,
                self.residual_vs_fitted_canvas,
                x_all_reps,
                y_all_reps,
                A, B, C, D
                )

            # Store analysis results on the instance (for future features)
            self.filepath = filepath
            self.x_axis = x_axis
            self.y_axis = y_axis
            self.A = A
            self.B = B
            self.C = C
            self.D = D
            self.unk_rep_x = unk_rep_x
            self.unk_rep_y = unk_rep_y
            self.unk_mean_x = unk_mean_x
            self.unk_mean_y = unk_mean_y
            self.results = results
            self.calibration_groups = calibration_groups
            self.calibration_stats = calibration_stats
            self.LLOQ = lloq
            self.ULOQ = uloq
            self.r2 = r2
            self.sse = sse
            self.residual_sd = residual_sd

            # -----------------------------------------------------------
            # 3) Unknown table (with LOQ-based status)
            # -----------------------------------------------------------
            unknown_data_table = unknown_table(results)
            unknown_data_table = add_unknown_status_column(
                unknown_data_table, lloq, uloq
            )
            self.unknown_data_table = unknown_data_table
            fill_table_widget(self.unknown_table, unknown_data_table)

            # -----------------------------------------------------------
            # 4) Calibration table (formatted from calibration_stats)
            # -----------------------------------------------------------
            calibration_table_dict = calibration_table(calibration_stats)
            self.calibration_table_dict = calibration_table_dict
            fill_table_widget(self.calibration_data_table, calibration_table_dict)

            # -----------------------------------------------------------
            # 5) Parameter table (4PL params + LOQ summary)
            # -----------------------------------------------------------
            params_dict = params_table_builder(A, B, C, D, uloq, lloq, r2, sse, residual_sd)
            fill_table_widget(self.params_table, params_dict)

        print("Finished analysis. Unknown samples:", len(self.results))


    def export_csv(self):
        if not hasattr(self, "results"):
            self.statusBar().showMessage("No data loaded yet.", 3000)
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "",
            "CSV Files (*.csv)",
        )

        if filepath:
            export_csv(
                filepath,
                self.A, self.B, self.C, self.D,
                self.r2, self.sse, self.residual_sd,
                self.LLOQ, self.ULOQ,
                self.unknown_data_table,
                self.calibration_table_dict,
            )
            self.statusBar().showMessage("Exported to " + filepath, 5000)