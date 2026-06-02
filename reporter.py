"""
reporter.py

Formatting and table-building utilities for the 4P assay tool.

This module is **presentation-only**:
- Takes numeric / structured results from `analysis.py`
- Builds dicts that describe tables: {"headers": [...], "rows": [[...], ...]}
- Helps populate Qt `QTableWidget` instances from those dicts
"""

from helpers.helper_fnx import cv_calc
from PySide6.QtWidgets import QTableWidgetItem




# ===================================================================
# Unknown samples table
# ===================================================================

def unknown_table(results, sample_outliers):
    """
    Build a table-dict summarizing unknown sample concentrations.

    Parameters
    ----------
    results : dict
        Mapping sample_id -> {
            "replicate_concentrations": [float, ...],
            "mean_concentration": float,
        }

    Returns
    -------
    dict
        {
          "headers": ["Sample ID", "N Reps", "Mean", "CV%", "Min", "Max", "Outliers"],
          "rows": [
            [sample_id, n_reps, mean, cv, min_val, max_val, outliers],
            ...
          ]
        }
    """
    table_rows = []
    for sample_id, info in results.items():
        reps = info["replicate_concentrations"]
        n_reps = len(reps)
        mean = round(info["mean_concentration"], 1)
        cv = round(cv_calc(reps), 1)
        minimum = round(min(reps), 1)
        maximum = round(max(reps), 1)
        outliers = sample_outliers.get(sample_id, [])
        outlier_display = "---" if len(outliers) == 0 else str(outliers)

        table_rows.append([
            sample_id,
            int(n_reps),
            float(mean),
            float(cv),
            float(minimum),
            float(maximum),
            outlier_display
        ])
    

    table_dict = {
        "headers": ["Sample ID", "N Reps", "Mean", "CV%", "Min", "Max", "Outliers"],
        "rows": table_rows,
    }
    return table_dict


# ===================================================================
# Calibration table (formatting only – stats come from analysis.py)
# ===================================================================

def calibration_table(calibration_stats, cal_outliers):
    """
    Build a table-dict summarizing calibration performance.

    Parameters
    ----------
    calibration_stats : dict Mapping calibrator_id -> 
        {
            "level": float,
            "n_reps": int,
            "mean_signal": float,
            "cv": float,
            "back_calc": float or None,
            "percent_recovery": float or None,
            "Outliers" : list
        }

    Returns
    -------
    dict
        {
          "headers": [...],
          "rows": [[...], ...]
        }
    """
    headers = [
        "Calibrator ID",
        "Level",
        "N Reps",
        "Signal Mean",
        "CV%",
        "Concentration Average",
        "% Recovery",
        "Outliers"
    ]

    table_rows = []

    for calibrator_id, stats in calibration_stats.items():
        level               = stats["level"]
        n_reps              = stats["n_reps"]
        mean_signal         = stats["mean_signal"]
        cv                  = stats["cv"]
        back_calc           = stats["back_calc"]
        percent_recovery    = stats["percent_recovery"]
        calibration_outliers = cal_outliers.get(calibrator_id, {}).get("outliers", [])
        cal_outlier_display = "---" if len(calibration_outliers) == 0 else str(calibration_outliers)

        # Display-only formatting
        level_disp = round(level, 2) if level is not None else "---"
        mean_disp  = round(mean_signal, 4) if mean_signal is not None else "---"
        cv_disp    = round(cv, 2) if cv is not None else "---"

        if back_calc is None or percent_recovery is None:
            back_disp = "---"
            rec_disp  = "---"
        else:
            back_disp = round(back_calc, 2)
            rec_disp  = round(percent_recovery, 1)

        table_rows.append([
            calibrator_id,
            level_disp,
            n_reps,
            mean_disp,
            cv_disp,
            back_disp,
            rec_disp,
            cal_outlier_display
        ])

    return {
        "headers": headers,
        "rows": table_rows,
    }


# ===================================================================
# Generic helper: dict -> QTableWidget
# ===================================================================

def fill_table_widget(table_widget, data_table):
    """
    Populate a QTableWidget from a table-dict.

    Parameters
    ----------
    table_widget : QTableWidget
        The Qt table widget to fill.
    data_table : dict
        {
          "headers": [...],
          "rows": [[...], ...]
        }
    """
    headers = data_table["headers"]
    rows = data_table["rows"]

    table_widget.setColumnCount(len(headers))
    table_widget.setHorizontalHeaderLabels(headers)

    table_widget.setRowCount(len(rows))
    for r_idx, row in enumerate(rows):
        for c_idx, value in enumerate(row):
            table_widget.setItem(r_idx, c_idx, QTableWidgetItem(str(value)))


# ===================================================================
# LOQ determination (based on formatted calibration table)
# ===================================================================

def determine_loq(cal_table_dict):
    """
    Derive estimated LLOQ and ULOQ from a *formatted* calibration table.

    Rule (configurable later):
      - ignore level == 0
      - CV% < 20
      - 80 < % Recovery < 120

    Parameters
    ----------
    cal_table_dict : dict
        The same dict you would pass to fill_table_widget() for the
        calibration table.

    Returns
    -------
    tuple
        (uloq, lloq) where each is a float or None.
    """
    passing_levels = []

    headers = cal_table_dict["headers"]
    level_idx = headers.index("Level")
    cv_idx = headers.index("CV%")
    rec_idx = headers.index("% Recovery")

    for row in cal_table_dict["rows"]:
        if row[level_idx] == 0:
            continue
        if row[cv_idx] < 20 and 80 < row[rec_idx] < 120:
            passing_levels.append(row)

    levels = [row[level_idx] for row in passing_levels]

    if len(levels) > 0:
        uloq = max(levels)
        lloq = min(levels)
    else:
        uloq = None
        lloq = None

    return uloq, lloq


# ===================================================================
# Unknown status column (ND / Below LOQ / Above LOQ / In Range)
# ===================================================================

def add_unknown_status_column(unknown_table_dict, lloq, uloq):
    """
    Placeholder definition (overridden by the implementation below).

    Kept for compatibility with your original file layout.
    """
    pass


def params_table_builder(A, B, C, D, uloq=None, lloq=None, r2 = None, sse = None, residual_sd = None):
    """
    Build the parameter table (4PL params + optional LOQs).

    Parameters
    ----------
    A, B, C, D : float
        4PL parameters.
    uloq, lloq : float or None
        Estimated LOQs from LOQ determination.

    Returns
    -------
    dict
        {
          "headers": ["Parameter", "Value"],
          "rows": [[name, value], ...]
        }
    """
    table_dict = {
        "headers": ["Parameter", "Value"],
        "rows": [
            ["A (Low)",   round(A, 4)],
            ["B (Slope)", round(B, 4)],
            ["C (EC50)",  round(C, 4)],
            ["D (High)",  round(D, 4)],
        ],
    }

    rows = table_dict["rows"]

    if lloq is not None:
        rows.append(["Estimated LLOQ", lloq])
    if uloq is not None:
        rows.append(["Estimated ULOQ", uloq])
    if r2 is not None:
        rows.append(["R²", round(r2, 4)])
    if sse is not None:
        rows.append(["SSE", round(sse, 4)])
    if residual_sd is not None:
        rows.append(["Residual SD", round(residual_sd, 4)])

    return table_dict


# Adding status column for unknowns based on LOQs
def add_unknown_status_column(unknown_table_dict, lloq, uloq):
    """
    Append a 'Status' column to the unknown table-dict.

    Status rules
    ------------
    - If mean is NaN/None      -> "ND"
    - If mean < LLOQ           -> "Below LOQ"
    - If mean > ULOQ           -> "Above LOQ"
    - Otherwise                -> "In Range"

    Parameters
    ----------
    unknown_table_dict : dict
        Table dict from unknown_table().
    lloq, uloq : float or None
        Estimated LOQ bounds.

    Returns
    -------
    dict
        Same dict object, with:
          - headers += ["Status"]
          - each row extended with status string
    """
    MEAN_IDX = 2  # index of "Mean" in each row

    unknown_table_dict["headers"].append("Status")

    new_rows = []
    for row in unknown_table_dict["rows"]:
        mean_val = row[MEAN_IDX]

        # NaN check: (mean_val != mean_val) is True only for NaN
        if mean_val is None or mean_val != mean_val:
            status = "ND"
        elif lloq is not None and mean_val < lloq:
            status = "Below LOQ"
        elif uloq is not None and mean_val > uloq:
            status = "Above LOQ"
        else:
            status = "In Range"

        new_rows.append(row + [status])

    unknown_table_dict["rows"] = new_rows
    return unknown_table_dict