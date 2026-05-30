"""
analysis.py

High-level analysis pipeline for the 4P Assay Tool.

Responsibilities:
- Load assay data from CSV (via data_loader).
- Fit a 4-parameter logistic (4PL) curve to the calibration data.
- Convert unknown sample signals into concentrations.
- Generate predicted signals for plotting.
- Compute calibration statistics and simple LLOQ/ULOQ estimates.
"""

from data_loader import load_assay_csv
from model_4pl import fit_4pl, four_pl, concentration_from_signal, model_diagnostics
from helpers.helper_fnx import sd_calc, cv_calc  # sd_calc unused currently, but kept


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def run_analysis(filepath):
    """
    Run the full analysis pipeline for a given assay CSV.

    Parameters
    ----------
    filepath : str
        Path to the CSV file containing assay data.

    Returns
    -------
    x_axis : list[float]
        Sorted calibrator concentrations used for fitting.
    y_axis : list[float]
        Mean calibrator signals, aligned with x_axis.
    A, B, C, D : float
        4PL fit parameters.
    unk_rep_x : list[float]
        Back-calculated concentrations for all unknown replicates.
    unk_rep_y : list[float]
        Predicted signals for each replicate concentration (for plotting).
    unk_mean_x : list[float]
        Mean back-calculated concentration for each unknown sample.
    unk_mean_y : list[float]
        Predicted signal at each mean concentration (for plotting).
    results : dict
        Unknown sample results:
        {sample_id: {"replicate_concentrations": [...],
                     "mean_concentration": float}, ...}
    calibration_groups : dict
        Raw calibrator grouping from data_loader:
        {calib_id: {"concentration": float, "signals": [...]}, ...}
    calibration_stats : dict
        Per-calibrator statistics:
        {calib_id: {"level", "n_reps", "mean_signal", "cv",
                    "back_calc", "percent_recovery"}, ...}
    uloq : float | None
        Estimated upper limit of quantitation based on simple rules.
    lloq : float | None
        Estimated lower limit of quantitation based on simple rules.
    """
    # -----------------------------------------------------------------------
    # 1) Load data from CSV
    # -----------------------------------------------------------------------
    x_axis, y_axis, unknown_groups, calibration_groups = load_assay_csv(filepath)

    # -----------------------------------------------------------------------
    # 2) Prepare data for 4PL fitting (skip x=0 for numerical stability)
    # -----------------------------------------------------------------------
    x_fit = []
    y_fit = []

    for x, y in zip(x_axis, y_axis):
        if x > 0:
            x_fit.append(x)
            y_fit.append(y)

    # Fit the 4PL model: y = 4PL(x; A, B, C, D)
    A, B, C, D = fit_4pl(x_fit, y_fit)

    #3 - Prepare data (all replicates) for r_squared calculation
    # Updates on 24May26
    # In analysis.py, after fit_4pl, instead of using x_fit and y_fit you'd unpack 
    # all individual replicates from calibration_groups- ADDED ON 24MAY26


    # specifically for r2 analysis, unpacking all individual replicates from calibration_groups
    x_all_reps = []
    y_all_reps = []

    for calib_id, info in calibration_groups.items():
        conc = info["concentration"]
        signals = info["signals"]
        if conc > 0:
            for signal in signals:
                x_all_reps.append(conc)
                y_all_reps.append(signal)

    r2, sse, residual_sd = model_diagnostics(x_all_reps, y_all_reps, A, B, C, D)

    # -----------------------------------------------------------------------
    # 4) Process unknown samples (back-calculate concentrations)
    # -----------------------------------------------------------------------
    results = {}      # per-sample concentration results
    unk_rep_x = []    # all replicate concentrations (for plotting)
    unk_rep_y = []    # predicted signals for each replicate
    unk_mean_x = []   # mean concentration per sample
    unk_mean_y = []   # predicted signal at each mean concentration

    # Back-calc each unknown signal to a concentration and summarize
    for sample_id, info in unknown_groups.items():
        replicate_signals = info["signals"]
        conc = []

        for y_obs in replicate_signals:
            replicate_conc = concentration_from_signal(y_obs, A, B, C, D)
            conc.append(replicate_conc)

        mean_conc = sum(conc) / len(conc)

        results[sample_id] = {
            "replicate_concentrations": conc,
            "mean_concentration": mean_conc,
        }

    # Flatten replicate concentrations and means for plotting
    for sample_id, info in results.items():
        rep = info["replicate_concentrations"]
        unk_rep_x.extend(rep)

    for sample_id, info in results.items():
        conc_mean = info["mean_concentration"]
        unk_mean_x.append(conc_mean)

    # Predict signals at those concentrations using the fitted 4PL
    for rep in unk_rep_x:
        pred_signal = four_pl(rep, A, B, C, D)
        unk_rep_y.append(pred_signal)

    for conc_mean in unk_mean_x:
        pred_signal = four_pl(conc_mean, A, B, C, D)
        unk_mean_y.append(pred_signal)

    # -----------------------------------------------------------------------
    # 5) Compute calibration statistics + simple LOQ estimates
    # -----------------------------------------------------------------------
    calibration_stats = {}
    passing_levels = []  # for LOQ determination

    for calib_id, info in calibration_groups.items():
        level = info["concentration"]
        signals = info["signals"]

        n_reps = len(signals)
        if n_reps == 0:
            mean_signal = float("nan")
            cv = float("nan")
        else:
            mean_signal = sum(signals) / n_reps
            cv = cv_calc(signals) if n_reps > 1 else 0.0

        if level == 0:
            back_calc = None
            percent_recovery = None
        else:
            back_calc = concentration_from_signal(mean_signal, A, B, C, D)
            percent_recovery = (back_calc / level) * 100.0

        calibration_stats[calib_id] = {
            "level":            level,
            "n_reps":           n_reps,
            "mean_signal":      mean_signal,
            "cv":               cv,
            "back_calc":        back_calc,
            "percent_recovery": percent_recovery,
        }

        # Simple LOQ rule of thumb:
        # - ignore level 0
        # - CV < 20%
        # - recovery between 80–120%
        if (
            level != 0
            and cv < 20
            and percent_recovery is not None
            and 80 < percent_recovery < 120
        ):
            passing_levels.append(level)

    if passing_levels:
        lloq = min(passing_levels)
        uloq = max(passing_levels)
    else:
        lloq = None
        uloq = None

    # -----------------------------------------------------------------------
    # 6) Return everything the GUI / reporter needs
    # -----------------------------------------------------------------------
    return (
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

    )