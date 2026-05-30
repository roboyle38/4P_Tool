"""
plotter.py

Plotting utilities for the 4P assay tool.
- plot_full_calibration: draws the fitted curve and unknowns into a Qt canvas.
"""

import matplotlib.pyplot as plt
import numpy as np
from model_4pl import four_pl

# ======================================================================
# Qt-embedded calibration plot (for the GUI)
# ======================================================================

def plot_full_calibration(
    figure,
    canvas,
    x_axis,
    y_axis,
    A,
    B,
    C,
    D,
    unk_rep_x,
    unk_rep_y,
    unk_mean_x,
    unk_mean_y,
    lloq,
    uloq
):
    """
    Draw the fitted 4PL curve and unknowns into a Qt-embedded Matplotlib canvas.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The Matplotlib Figure used by the Qt canvas.
    canvas : FigureCanvas
        The Qt-compatible canvas wrapping the figure.
    x_axis, y_axis : list[float]
        Calibrator concentrations and mean signals.
    A, B, C, D : float
        4PL parameters.
    unk_rep_x, unk_rep_y : list[float]
        Back-calculated concentrations and predicted signals for unknown replicates.
    unk_mean_x, unk_mean_y : list[float]
        Mean concentrations and predicted signals for each unknown sample.
    uloq, lloq : 
    
    """
    # ------------------------------------------------------------------
    # 1) Build smooth curve in log space (skip x <= 0)
    # ------------------------------------------------------------------
    x_vals = np.array(x_axis, dtype=float)
    positive = x_vals > 0
    x_min = x_vals[positive].min()
    x_max = x_vals[positive].max()

    smooth_x = np.logspace(
        np.log10(x_min),
        np.log10(x_max),
        200,
    )
    smooth_y = [four_pl(x, A, B, C, D) for x in smooth_x]

    # ------------------------------------------------------------------
    # 2) Draw everything on the figure/canvas
    # ------------------------------------------------------------------
    figure.clear()
    ax = figure.add_subplot(111)

    # Fitted 4PL curve
    ax.plot(smooth_x, smooth_y)
    ax.set_xscale("log")
    ax.set_xlabel("Concentration")
    ax.set_ylabel("Signal")

    # Unknown replicates and means
    ax.scatter(
        unk_rep_x,
        unk_rep_y,
        marker="+",
        color="red",
        label="Unknown Replicates",
        s=20,
    )
    ax.scatter(
        unk_mean_x,
        unk_mean_y,
        marker="+",
        color="black",
        label="Unknown Mean",
        s=160,
    )

    ax.axvspan(lloq, uloq, alpha = 0.3, color = "lightgrey", label = "Approximate Calibration Range")
    ax.legend(fontsize=8, loc="best")

    # Trigger redraw in the Qt canvas
    figure.tight_layout()
    canvas.draw()


def plot_residuals(figure, canvas, x_all_reps, y_all_reps, A, B, C, D):
    """
    Plot residuals vs concentration for all calibrator replicates.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
    canvas : FigureCanvas
    x_all_reps : list[float]
        Calibrator concentrations (one per replicate)
    y_all_reps : list[float]
        Calibrator signals (one per replicate)
    A, B, C, D : float
        4PL parameters
    """

    # Calculate residuals
    residuals = []
    for x, y in zip(x_all_reps, y_all_reps):
        y_pred = four_pl(x, A, B, C, D)
        relative_residual = ((y - y_pred) / y_pred) * 100
        residuals.append(relative_residual)

    figure.clear()
    ax = figure.add_subplot(111)

    # Plot residuals
    ax.scatter(x_all_reps, residuals, color="steelblue", s=40, zorder=3)

    # Zero reference line
    ax.axhline(y=0, color="red", linewidth=1, linestyle="--")

    ax.set_xscale("log")
    ax.set_xlabel("Concentration")
    ax.set_ylabel("Relative Residual (%)")
    ax.set_title("Residuals vs Concentration")

    figure.tight_layout(pad=2.0)
    canvas.draw()

def plot_residuals_vs_fitted(figure, canvas, x_all_reps, y_all_reps, A, B, C,D):

    '''
    Plot residuals vs fitted values for all calibrator replicates
    X axis: the predicted signal(y-pred)
    Y axis: the relative residual %
        '''

    residuals = []
    y_pred_list = []
    for x, y in zip(x_all_reps, y_all_reps):
        y_pred = four_pl(x, A, B, C, D)
        y_pred_list.append(y_pred)
        relative_residual = ((y - y_pred) / y_pred) * 100
        residuals.append(relative_residual)
    
    figure.clear()
    ax = figure.add_subplot(111)

    # Plot residuals vs fitted values
    ax.scatter(y_pred_list, residuals, color ="steelblue", s=40, zorder = 3)
    ax.axhline(y=0, color="red", linewidth=1, linestyle="--")

    ax.set_xscale("linear")
    ax.set_xlabel("Predicted Signal")
    ax.set_ylabel("Relative Residual (%)")
    ax.set_title("Predicted Signal vs Relative Residual")

    figure.tight_layout(pad = 2.0)
    canvas.draw()

    



