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
        sd = round(float(sd), 2)
    return sd


def cv_calc(list_of_numbers):
    sd = sd_calc(list_of_numbers)
    mean = sum(list_of_numbers)/len(list_of_numbers)
    cv = (sd / mean) * 100
    cv = round(cv, 10)
    return cv

list_of_numbers = [1, 2,7, 12.8888, 3, 3]

print(cv_calc(list_of_numbers))

