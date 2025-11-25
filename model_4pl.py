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