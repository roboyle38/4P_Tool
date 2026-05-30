from scipy.optimize import curve_fit
import numpy as np

def four_pl(x, A, B, C, D):
    # Condensed equation --> D + (A - D) / (1 + (x / C)**B)
    x = np.array(x, dtype=float)
    scaled = x / C
    powered = scaled ** B
    denom = 1.0 + powered
    frac = (A - D) / denom
    y = frac + D
    return y


def concentration_from_signal(y_obs, A, B, C, D):
    # Condensed equation --> C * (((A - D) / (y_obs - D) - 1)**(1 / B))
    numerator = A - D
    denom = y_obs - D
    ratio = numerator / denom
    inner = ratio - 1.0
    exponent = 1.0 / B
    powered = inner ** exponent
    x = C * powered
    return x


def fit_4pl(x,y):
    # 1. choose initial guesses for A, B, C, D
    # 2. run a curve-fitting algorithm
    # 3. return the best-fit values (A, B, C, D)
    # A = lower_asymptote; B = slope_at_inflection_point; C = inflection_point; D = upper_asymptote
    x = np.array(x , dtype = float) # --> ensure X and Y are numeric arrays
    y = np.array(y, dtype = float)
    A_guess = min(y) # --> lower and upper asymptote guess required because nonlinear curve fitting needs a reasonable starting point
    D_guess = max(y)
    C_guess = np.median(x)
    B_guess = 1.0
    p0 = [A_guess, B_guess, C_guess, D_guess] # <starting guess vector
    popt, pcov = curve_fit(four_pl, x, y, p0 = p0, maxfev = 10000)
    A, B, C, D = popt
    #popt = best fit for A, B, C, D
    #pcov = covariance matrix
    return A, B, C, D

# Generic R2 calculation - ADDED ON 24MAY26
# Note to remember - numpy is running a loop on every element in the array

def model_diagnostics(x, y, A, B, C, D):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    y_pred = four_pl(x, A, B, C, D)
    y_mean = np.mean(y)

    residuals = y - y_pred
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)

    r2 = 1 - (ss_res / ss_tot)
    sse = ss_res
    residual_sd = np.std(residuals, ddof=1)

    return r2, sse, residual_sd