
"""
data_loader.py

Utilities for reading 4P assay CSV files and transforming them into
structures used by the analysis pipeline.
"""

import csv

# ---------------------------------------------------------------------------
# Column mapping
# ---------------------------------------------------------------------------
# Maps logical field names used in the code to column names in the CSV.
# If your CSV headers ever change, you only update this dict.
column_map = {
    "sample_id": "sample_id",
    "role": "role",                  # "CAL" (calibrator) or "UNK" (unknown)
    "concentration": "concentration",
    "replicate_id": "replicate_id",
    "signal": "signal",
}

# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------
def load_assay_csv(filepath):
    """
    Load an assay CSV file and return data ready for 4PL fitting.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.

    Returns
    -------
    x_axis : list[float]
        Sorted list of calibrator concentrations.
    y_axis : list[float]
        Mean signal for each calibrator concentration, sorted to match x_axis.
    unknown_groups : dict
        {sample_id: {"signals": [signal_1, signal_2, ...]}, ...}
    calibration_groups : dict
        {sample_id: {"concentration": conc, "signals": [..]}, ...}
    """
    with open(filepath, newline="", encoding="UTF-8") as f:
        # DictReader yields each row as {column_name: value, ...}
        reader = csv.DictReader(f)

        calibration_rows = []
        unknown_rows = []
        calibration_groups = {}
        unknown_groups = {}

        # -------------------------------------------------------------------
        # First pass: group signals by sample_id for CAL and UNK
        # -------------------------------------------------------------------
        for row in reader:
            # Extract raw values from the CSV row using the column_map
            sample_id = row[column_map["sample_id"]]
            role = row[column_map["role"]]
            concentration_str = row[column_map["concentration"]]
            rep_id = row[column_map["replicate_id"]]
            signal_str = row[column_map["signal"]]

            # Parse concentration (may be blank for unknowns)
            if concentration_str != "":
                concentration = float(concentration_str)
            else:
                concentration = None

            # Parse signal; if blank, we leave `signal` undefined here
            if signal_str != "":
                signal = float(signal_str)

            # Split into calibrators vs unknowns
            if role == "CAL":
                calibration_rows.append(row)

                if sample_id not in calibration_groups:
                    calibration_groups[sample_id] = {
                        "concentration": None,
                        "signals": [],
                    }
                calibration_groups[sample_id]["concentration"] = concentration
                calibration_groups[sample_id]["signals"].append(signal)

            elif role == "UNK":
                unknown_rows.append(row)

                if sample_id not in unknown_groups:
                    unknown_groups[sample_id] = {"signals": []}
                unknown_groups[sample_id]["signals"].append(signal)

            else:
                # Non-CAL/UNK rows: currently ignored
                signal = None

    # -----------------------------------------------------------------------
    # Second pass: compute mean signal per calibrator concentration
    # -----------------------------------------------------------------------
    concentration_means = {}  # {concentration: mean_signal}

    for sample_id, info in calibration_groups.items():
        concentration = info["concentration"]
        signals = info["signals"]
        final_mean = sum(signals) / len(signals)
        concentration_means[concentration] = final_mean

    # Build x/y lists from the concentration_means dict
    x_axis = []
    y_axis = []
    for conc, mean_signal in concentration_means.items():
        x_axis.append(conc)
        y_axis.append(mean_signal)

    # Keep x/y in ascending order of concentration
    pairs = [(x_axis[i], y_axis[i]) for i in range(len(x_axis))]
    pairs.sort()
    x_axis = [p[0] for p in pairs]
    y_axis = [p[1] for p in pairs]

    return x_axis, y_axis, unknown_groups, calibration_groups


# ---------------------------------------------------------------------------
# Local test harness (only runs when you execute this file directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    filepath = 'C:/Users/roboy/iCloudDrive/Desktop/Python/Projects/4P_Tool/assets/sample_data/Assay_dataset_2.csv'
    result = load_assay_csv(filepath)
    x_axis, y_axis, unknown_groups, calibration_groups = result
    print(f'x_axis = {x_axis}')
    print(f'y_axis = {y_axis}')
    print(f'Unknown groups = {unknown_groups}')
    print(f'Calibration groups = {calibration_groups}')
