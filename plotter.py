print("starting plotter. py")

import matplotlib.pyplot as plt
import numpy as np
from model_4pl import four_pl
from analysis import run_analysis

def plot_calibration(x_axis, y_axis, A, B, C, D,
                     unk_rep_x, unk_rep_y,
                     unk_mean_x, unk_mean_y):
    plt.figure()

    plt.scatter(x_axis, y_axis, marker = "o", color = "blue",
                 label = "Calibrator Average", s = 50)
    
    x_curve = np.linspace(min(x_axis), max(x_axis), 200)
    y_curve = four_pl(x_curve, A, B, C, D)
    plt.plot(x_curve, y_curve)
    plt.scatter(unk_rep_x, unk_rep_y, marker = "+", color="red",
                 label="Unknown Replicates", s = 20)
    plt.scatter(unk_mean_x, unk_mean_y, marker = "+", color= "black",
                 label = "Unknown Mean", s = 160)
    plt.legend(fontsize = 8, loc = "best")
    plt.xlabel("Concentration"),plt.ylabel("Signal")



