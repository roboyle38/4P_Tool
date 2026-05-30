"""
exporter.py

Handles exporting analysis results to CSV files.
"""

import csv
from datetime import datetime


def export_csv(filepath, A, B, C, D, r2, sse, residual_sd, lloq, uloq, unknown_data_table, calibration_table_dict):
    """
    Export analysis results to a structured CSV file.

    Parameters
    ----------
    filepath : str
        Path to save the CSV file.
    A, B, C, D : float
        4PL parameters.
    r2, sse, residual_sd : float
        Model diagnostics.
    lloq, uloq : float or None
        Estimated LOQs.
    unknown_table_dict : dict
        Table dict from unknown_table().
    calibration_table_dict : dict
        Table dict from calibration_table().
    """
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(["4P Assay Tool Export"])
        writer.writerow(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")])
        writer.writerow([])

        # Model parameters
        writer.writerow(["--- Model Parameters ---"])
        writer.writerow(["Parameter", "Value"])
        writer.writerow(["A (Low)",      round(A, 4)])
        writer.writerow(["B (Slope)",    round(B, 4)])
        writer.writerow(["C (EC50)",     round(C, 4)])
        writer.writerow(["D (High)",     round(D, 4)])
        writer.writerow(["R2",           round(r2, 4)])
        writer.writerow(["SSE",          round(sse, 4)])
        writer.writerow(["Residual SD",  round(residual_sd, 4)])
        writer.writerow(["Estimated LLOQ", lloq if lloq is not None else "---"])
        writer.writerow(["Estimated ULOQ", uloq if uloq is not None else "---"])
        writer.writerow([])

        # Unknown samples
        writer.writerow(["--- Unknown Samples ---"])
        writer.writerow(unknown_data_table["headers"])
        for row in unknown_data_table["rows"]:
            writer.writerow(row)
        writer.writerow([])

        # Calibrators
        writer.writerow(["--- Calibrators ---"])
        writer.writerow(calibration_table_dict["headers"])
        for row in calibration_table_dict["rows"]:
            writer.writerow(row)