from data_loader import load_assay_csv
from model_4pl import fit_4pl, four_pl, concentration_from_signal
from helpers.helper_fnx import sd_calc, cv_calc


def run_analysis(filepath):

    data_to_analyze = load_assay_csv(filepath)
    x_axis, y_axis , unknown_groups, calibration_groups = data_to_analyze

    A, B, C, D = fit_4pl(x_axis, y_axis)

    results = {}
    unk_rep_x = []
    unk_rep_y = []
    unk_mean_x = []
    unk_mean_y = []

    for sample_id, info in unknown_groups.items():
    # Convert each unknown-sample signal to a concentration (clamped to the
    # calibration range), store all replicate concentrations, and compute the mean.
        replicate = info["signals"]
        conc = []

        for y_obs in replicate: # Min and max values clamped by asymptotes
            if y_obs <= A:
                replicate_conc = min(x_axis)
            elif y_obs >= D:
                replicate_conc = max(x_axis)
            else:
                replicate_conc = concentration_from_signal(y_obs, A, B, C, D)
            conc.append(replicate_conc)
        mean_conc = sum(conc) / len(conc)
        results[sample_id] = {
            "replicate_concentrations" :conc, 
            "mean_concentration" :mean_conc
            }


    for sample_id, info in results.items():
        rep = info["replicate_concentrations"]
        unk_rep_x.extend(rep)
    for sample_id, info in results.items():
        conc_mean = info["mean_concentration"]
        unk_mean_x.append(conc_mean)
    for rep in unk_rep_x:
        pred_signal = four_pl(rep, A, B, C, D)
        unk_rep_y.append(pred_signal)
    for conc_mean in unk_mean_x:
        pred_signal = four_pl(conc_mean, A, B, C, D)
        unk_mean_y.append(pred_signal)

    return x_axis, y_axis, A, B, C, D, unk_rep_x, unk_rep_y, unk_mean_x, unk_mean_y, results, calibration_groups

