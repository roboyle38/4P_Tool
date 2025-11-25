from analysis import run_analysis
from plotter import plot_calibration
from reporter import unknown_table, calibration_table
from data_loader import load_assay_csv


def main():
    # === 1. Specify the CSV file ===
    filepath = "/Users/robertboyle/Desktop/Python/Projects/4P_Tool/assets/sample_data/Assay_dataset_2.csv"

    # === 2. Run the full analysis pipeline ===
    (x_axis, y_axis,
     A, B, C, D,
     unk_rep_x, unk_rep_y,
     unk_mean_x, unk_mean_y,
     results, calibration_groups) = run_analysis(filepath)

    table = unknown_table(results)
    cal_table = calibration_table(calibration_groups, A, B, C, D, units = "ng/mL")

    # === 3. Plot calibration curve + unknown samples ===
    plot_calibration(
        x_axis, y_axis, A, B, C, D,
        unk_rep_x, unk_rep_y,
        unk_mean_x, unk_mean_y
    )
    
    print(cal_table)

if __name__ == "__main__":
    main()


