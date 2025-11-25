# Goal - Make a blank window appear from main_window.py.
# A GUI window in Qt needs to be a class that inherits from QMainWindow.


#patchwork
import os
import sys

# 1) Find the folder that *this* file (main_window.py) is in
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 2) Go one level up: that’s your 4P_Tool project root
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
# 3) Tell Python to also look there for imports
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
# 4) Now this will work:
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
    QPushButton)
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from plotter import plot_calibration
from model_4pl import four_pl
import numpy as np
from helpers.helper_fnx import cv_calc
from reporter import unknown_table



"""	
•	PySide6 is the Python binding for the Qt GUI framework.
It is the library that creates windows, buttons, layouts, tables, etc.
•	QtWidgets is a module inside PySide6 that contains all the standard GUI widgets:
•	QMainWindow (main app window)
•	QPushButton (button)
•	QLabel (text label)
•	QTableWidget (table)
•	QVBoxLayout (vertical layout manager)
•	QMainWindow is the specific widget class that represents a full application window."""

    #A class is a blueprint that is a way to package data, behaviort, and state. 
    #Mainwindow inherits from QMainWindow
    
class MainWindow(QMainWindow):
    
    """ This is the constructor for your class"""
    def __init__(self):
        #this means give me the parent class - run QMainWindow's constructor. 
        super().__init__()
        # self - window instance; .setwindowTitle - method provided by QMainWindow
        self.setWindowTitle("4P Assay Tool")
        self.resize(900,600)
        self.central = QWidget ()
        self.layout = QVBoxLayout()
        self.central.setLayout(self.layout)
        self.setCentralWidget(self.central)
        
        #Status Bar
        self.status_label = QLabel("No file loaded.")
        self.layout.addWidget(self.status_label)
        self.statusBar().showMessage("Ready")
        
        #Buttons
        self.button_row = QHBoxLayout()
        self.load_csv = QPushButton("Load CSV")
        self.clear_button = QPushButton("Clear Plot")
        self.button_row.addWidget(self.load_csv)
        self.button_row.addWidget(self.clear_button)
        self.layout.addLayout(self.button_row)
        self.load_csv.clicked.connect(self.open_csv)
        self.clear_button.clicked.connect(self.on_clear_clicked)
        
        # Build the menu bar and menus
        self._create_menus()

        """creating plot"""
        #create a blank Matplotlib "page" where plots will go later.
        self.figure = Figure()
        #Wraps the figure in a Qt-compatible widget so it can be shown inside the GUI
        self.canvas = FigureCanvas(self.figure)
        # Tells Qt to put this Matplotlib canvas into the main vertical layout.
        self.layout.addWidget(self.canvas)
        # Adding the unknown table
        self.unknown_table = QTableWidget()
        self.unknown_table.setColumnCount(6)
        self.unknown_table.setHorizontalHeaderLabels(["Sample ID", "N Reps", "Mean", "CV%", "Min", "Max"])
        self.layout.addWidget(self.unknown_table)
        

    def on_clear_clicked(self):
        """Clear the plot area."""
        self.figure.clear()
        self.canvas.draw()
        self.statusBar().showMessage("Plot cleared", 3000)


    def _create_menus(self):
        menubar = self.menuBar()

        # ---- File menu ----
        file_menu = menubar.addMenu("File")

        # Open CSV
        open_action = QAction("Open CSV", self)
        open_action.triggered.connect(self.open_csv)  
        file_menu.addAction(open_action) 

        # Quit
        quit_action = QAction("Quit", self)
        quit_action.setMenuRole(QAction.NoRole)  # tell macOS not to move it
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)


# Defines an instance method on MainWindow. 
# This must exist because your menu action is calling self.open_csv
# opens csv behind the scenes. After we need to hook that up to widgets
    def open_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV file",
            "",
            "CSV Files (*.csv)"
        )
        if filepath:
            print("User opened:", filepath)
            self.status_label.setText("Loaded: " + filepath)
            self.status_label.setText(f"Loaded: {os.path.basename(filepath)}")
            self.statusBar().showMessage("Running analysis...", 1000)
            self.statusBar().showMessage("Analysis complete.", 50000)

                    # TEMP: run your analysis pipeline
            (
            x_axis,
            y_axis,
            A, B, C, D,
            unk_rep_x, unk_rep_y,
            unk_mean_x, unk_mean_y,
            results,
            calibration_groups
            ) = run_analysis(filepath)

            x_vals = np.array(x_axis, dtype =float)
            positive = x_vals > 0
            x_min = x_vals[positive].min()
            x_max = x_vals[positive].max()
            smooth_x = np.logspace(
                np.log10(x_min),
                np.log10(x_max),
                200
                )
            smooth_y = [four_pl(x, A, B, C, D) for x in smooth_x]

            plot_calibration(
            x_axis, y_axis,
            A, B, C, D,
            unk_rep_x, unk_rep_y,
            unk_mean_x, unk_mean_y
            )

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(smooth_x, smooth_y)
            ax.set_xscale("log")
            ax.set_xlabel("Concentration")
            ax.set_ylabel("Signal")
            ax.set_title("Calibration Curve")
            ax.scatter(unk_rep_x, unk_rep_y, marker = "+", color="red",
                 label="Unknown Replicates", s = 20)
            ax.scatter(unk_mean_x, unk_mean_y, marker = "+", color= "black",
                 label = "Unknown Mean", s = 160)
            ax.legend(fontsize = 8, loc = "best")
            self.canvas.draw()


            #Creating unknown data table
            unknown_data_table = unknown_table(results)
            self.unknown_table.setColumnCount(len(unknown_data_table["headers"]))
            self.unknown_table.setHorizontalHeaderLabels(unknown_data_table["headers"])
            #fill the table rows
            rows = unknown_data_table["rows"]
            self.unknown_table.setRowCount(len(rows))

            for sample, info in enumerate(rows):
                for c, value in enumerate(info):
                    self.unknown_table.setItem(sample, c, QTableWidgetItem(str(value)))


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
        
        print("Finished analysis. Unknown samples:", len(results))

