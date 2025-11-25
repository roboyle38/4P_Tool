from helpers.helper_fnx import cv_calc
from analysis import run_analysis
from model_4pl import fit_4pl, four_pl, concentration_from_signal


# need to add to table a column indicating whether the sample is within range.
def unknown_table(results):
    table_rows = []
    for sample_id, info in results.items():
        n_reps = len(info['replicate_concentrations'])
        mean = round(info["mean_concentration"], 1)
        cv = round(cv_calc(info['replicate_concentrations']), 1)
        minimum = round(min(info['replicate_concentrations']), 1)
        maximum = round(max(info['replicate_concentrations']), 1)
        table_rows.append([sample_id, int(n_reps), float(mean), float(cv), float(minimum), float(maximum)])
    table_dict = { "headers" : ["Sample ID", "N Reps", "Mean", "CV%", "Min", "Max"], 
                    "rows": table_rows}
    return table_dict

def calibration_table(calibration_groups, A, B, C, D, units = "ng/mL"):
    # | Level | Nominal Conc | Mean Signal | CV% (Signal) | Back-Calc Conc | % Recovery |
    
    table_rows = []
    for calibrator_id, info in calibration_groups.items():
        level = round(info["concentration"], 2)
        #units???
        n_reps = len(info["signals"])
        signal_mean = round(sum(info["signals"]) / len(info["signals"]), 4)
        cv = round(cv_calc(info["signals"]), 2)
        if level == 0:
            back_calc = "---"
            percent_recovery = "---"
        else:
            back_calc = float(round(concentration_from_signal(signal_mean, A, B, C, D), 2))
            percent_recovery = float(round((back_calc / level) * 100, 1))            
        table_rows.append([calibrator_id, 
                           float(level), 
                           int(n_reps), 
                           float(signal_mean), 
                           float(cv), 
                           back_calc, 
                           percent_recovery])
        # % recovery
        table_dict = {"headers" : ["Calibrator ID", 
                    f"Level ({units})", 
                    "N Reps", 
                    "Signal Mean", 
                    "CV%", 
                    "Concentration Average", 
                    "% Recovery"], 
                    "rows": table_rows
                      }
        
    return table_dict

"""({'CAL_00': {'concentration': 0.0, 'signals': [0.018, 0.017, 0.019]}, 
'CAL_05': {'concentration': 0.5, 'signals': [0.032, 0.031, 0.035]}, 
'CAL_10': {'concentration': 1.0, 'signals': [0.051, 0.049, 0.053]}, 
'CAL_20': {'concentration': 2.0, 'signals': [0.088, 0.091, 0.087]}, 
'CAL_40': {'concentration': 4.0, 'signals': [0.145, 0.152, 0.149]}, 
'CAL_80': {'concentration': 8.0, 'signals': [0.255, 0.262, 0.249]}, 
'CAL_160': {'concentration': 16.0, 'signals': [0.445, 0.438, 0.461]}, 
'CAL_320': {'concentration': 32.0, 'signals': [0.76, 0.742, 0.771]}, 
'CAL_640': {'concentration': 64.0, 'signals': [1.115, 1.089, 1.124]}, 
'CAL_1280': {'concentration': 128.0, 'signals': [1.574, 1.602, 1.547]}, 
'CAL_2560': {'concentration': 256.0, 'signals': [1.942, 2.015, 1.983]}, 
'CAL_5120': {'concentration': 512.0, 'signals': [2.21, 2.185, 2.198]}}"""



#from ChatGPT - get rid of later
def print_table(table):
    headers = table["headers"]
    rows = table["rows"]

    # Convert everything to strings for sizing and printing
    rows_str = [[str(x) for x in row] for row in rows]
    headers_str = [str(h) for h in headers]

    # Compute column widths
    col_widths = []
    for col_idx in range(len(headers_str)):
        column_items = [headers_str[col_idx]] + [row[col_idx] for row in rows_str]
        max_width = max(len(item) for item in column_items)
        col_widths.append(max_width)

    # Build format string: left align first column, right align numbers
    fmt = " | ".join("{:<" + str(w) + "}" for w in col_widths)

    # Print header
    print(fmt.format(*headers_str))

    # Print separator
    print("-" * (sum(col_widths) + 3 * (len(col_widths) - 1)))

    # Print each row
    for row in rows_str:
        print(fmt.format(*row))


if __name__ == "__main__":
    # TEMPORARY DEBUGGING BLOCK
    from analysis import run_analysis
    
    filepath = "/Users/robertboyle/Desktop/Python/Projects/4P_Tool/assets/sample_data/Assay_dataset_2.csv"
    """# We get results EXACTLY like main.py does
    (
        _x, _y,
        A, B, C, D,
        unk_rep_x, unk_rep_y,
        unk_mean_x, unk_mean_y,
        results, calibration_groups
    ) = run_analysis(filepath)

    # Now test the reporter
    #table = unknown_table(results)
    #print_table(table)
    #cal_table = calibration_table(calibration_groups, A, B, C, D)
    #print(cal_table)
    print("\nDEBUG TABLE:\n", table)"""