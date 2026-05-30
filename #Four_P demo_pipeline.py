# demo_pipeline.py
"""
Minimal console demo of your 4P tool.

- Loads a CSV
- Runs run_analysis
- Builds the report tables
- Prints them to the terminal
"""

from analysis import run_analysis
from reporter import (
    unknown_table,
    calibration_table,
    params_table_builder,
    add_unknown_status_column,
)


# --- tiny helper to pretty-print a table_dict from reporter ---
def print_table_dict(table_dict, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    headers = table_dict["headers"]
    rows = table_dict["rows"]

    # simple column widths
    col_widths = []
    for i, h in enumerate(headers):
        col_vals = [str(r[i]) for r in rows]
        col_widths.append(max(len(h), *(len(v) for v in col_vals)))

    # format string
    fmt = " | ".join(f"{{:<{w}}}" for w in col_widths)

    # header
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 3 * (len(col_widths) - 1)))

    # rows
    for row in rows:
        print(fmt.format(*[str(v) for v in row]))


if __name__ == "__main__":
    # 1) pick a CSV (use the one you’ve been testing)
    filepath = (
        "/Users/robertboyle/Desktop/Python/Projects/4P_Tool/"
        "assets/sample_data/Assay_dataset_3.csv"
    )

    # 2) Run the analysis layer (NO GUI)
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
    ) = run_analysis(filepath)

    print("4PL parameters:")
    print(f"  A (Low)   = {A}")
    print(f"  B (Slope) = {B}")
    print(f"  C (EC50)  = {C}")
    print(f"  D (High)  = {D}")
    print(f"  LLOQ      = {lloq}")
    print(f"  ULOQ      = {uloq}")

    # 3) Build the same tables the GUI uses
    unk_tbl = unknown_table(results)
    unk_tbl = add_unknown_status_column(unk_tbl, lloq, uloq)

    cal_tbl = calibration_table(calibration_stats)

    params_tbl = params_table_builder(A, B, C, D, uloq, lloq)

    # 4) Print them to the console
    print_table_dict(params_tbl, "Parameter Table")
    print_table_dict(unk_tbl, "Unknown Samples")
    print_table_dict(cal_tbl, "Calibration Summary")


    """
    Dictionaries

    Dictionary name - Calibration Groups
    Location - Data Loader
    Outer - sample_id for calibrators
    Inner dict - numeric info for calibrators

    calibration_groups = {
    "CAL_00": {
        "concentration": 0.0,
        "signals": [0.018, 0.017, 0.019],
    },
    "CAL_05": {
        "concentration": 0.5,
        "signals": [0.032, 0.031, 0.035],
    },
    ...


    Dictionary name - unknown groups
    Location - data loader

    unknown_groups = {
    "S1": {
        "signals": [0.075, 0.071, 0.073],
    },
    "S2": {
        "signals": [0.24, 0.232, 0.246],
    },
    ...
}

    Dictionary - results
    Location - analysis.py

results = {
    "S1": {
        "replicate_concentrations": [0.9, 1.0, 0.95],
        "mean_concentration": 0.95,
    },
    "S2": {
        "replicate_concentrations": [3.8, 3.9, 4.0],
        "mean_concentration": 3.9,
    },
    ...
}

    Dictionary - calibration stats
    Location - analysis.py

    calibration_stats = {
    "CAL_00": {
        "level": 0.0,
        "n_reps": 3,
        "mean_signal": 0.018,
        "cv":  5.23,
        "back_calc": None,
        "percent_recovery": None,
    },
    "CAL_05": {
        "level": 0.5,
        "n_reps": 3,
        "mean_signal": 0.0327,
        "cv":  6.83,
        "back_calc": 0.47,
        "percent_recovery": 94.0,
    },
    ...
}


    Standardized Table Dictionary 

    Dictionary - Unknown Table Dict
    Built by - main_window -->. unknown_data_table = unknown_table(results)


    unknown_data_table = {
    "headers": ["Sample ID", "N Reps", "Mean", "CV%", "Min", "Max", "Status"],
    "rows": [
        ["S1", 3, 0.95,  4.2, 0.90, 1.00, "In Range"],
        ["S2", 3, 3.90,  6.1, 3.80, 4.05, "In Range"],
        ["S3", 3, 0.03, 18.0, 0.02, 0.04, "Below LOQ"],
        ["S4", 3, 500.0,  5.0, 480, 520, "Above LOQ"],
    ]
}

    Calibration Table

    calibration_table_dict = {
    "headers": [
        "Calibrator ID",
        "Level",
        "N Reps",
        "Signal Mean",
        "CV%",
        "Concentration Average",
        "% Recovery",
    ],
    "rows": [
        ["CAL_00",   0.00, 3, 0.0180,  5.23,   "---",   "---"],
        ["CAL_05",   0.50, 3, 0.0327,  6.83,   0.47,     94.0],
        ["CAL_10",   1.00, 3, 0.0510,  4.12,   1.05,    105.0],
        ...
    ]
}

    params_dict = {
    "headers": ["Parameter", "Value"],
    "rows": [
        ["A (Low)",        0.0123],
        ["B (Slope)",      1.5678],
        ["C (EC50)",      12.3456],
        ["D (High)",       2.3456],
        ["Estimated LLOQ", 0.50],
        ["Estimated ULOQ", 256.0],
    ]
}
    
Summary

CSV
  → load_assay_csv
      → calibration_groups (dict of dicts)
      → unknown_groups     (dict of dicts)
      → x_axis, y_axis
  → run_analysis
      → results (dict of dicts)
      → calibration_stats (dict of dicts)
      → uloq, lloq
      → unk_* arrays
  → reporter
      → unknown_table dict
      → calibration_table dict
      → params_table dict
  → MainWindow
      → fill Qt tables + plot


    
    """