from scipy import stats
import numpy as np

def sd_calc(list_of_numbers):
    if len(list_of_numbers) <= 1:
        sd = 0.0
    else:
        mean = sum(list_of_numbers) / len(list_of_numbers)
        squared_differences = []
        for number in list_of_numbers:
            difference_from_mean = number - mean
            squared_difference = difference_from_mean **2
            squared_differences.append(squared_difference)
        sum_of_squares = sum(squared_differences)
        variance = sum_of_squares / (len(list_of_numbers)-1)
        sd = variance ** 0.5
    return sd


def cv_calc(list_of_numbers):
    sd = sd_calc(list_of_numbers)
    mean = sum(list_of_numbers)/len(list_of_numbers)
    cv = (sd / mean) * 100
    return cv


"""
The Grubbs test function needs:
    1. A list of numbers
    2. A significance level
    3. Return the outlier values if one is found, or None

The G statistic is:
    G = max(|xi - mean|) / SD

Need to import scipy.stats




"""

def grubbs(list_of_numbers, alpha = 0.05):
    n = len(list_of_numbers)
    if n < 3:
        return None
    mean = sum(list_of_numbers) / n
    stdev = sd_calc(list_of_numbers)
    g_list = []
    for num in list_of_numbers:
        g = abs((num - mean) / stdev)
        g_list.append(g)
    g_max = max(g_list)
    g_max_index = g_list.index(g_max)

    t_crit = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    g_crit = ((n - 1) / np.sqrt(n)) * np.sqrt(t_crit**2 / (n - 2 + t_crit**2))

    if g_max > g_crit:
        return list_of_numbers[g_max_index]
    else:
        return None


def grubbs_esd(list_of_numbers, alpha=0.05):
    """
    Generalized ESD test - detects multiple outliers iteratively.
    Returns a list of outlier values.
    """
    remaining = list_of_numbers.copy()
    outliers = []
    max_outliers = len(list_of_numbers) - 2  # always keep at least 2

    for _ in range(max_outliers):
        if len(remaining) < 3:
            break
        result = grubbs(remaining, alpha)
        if result is not None:
            outliers.append(result)
            remaining.remove(result)
        else:
            break  # no more outliers found

    return outliers


