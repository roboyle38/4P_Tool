import csv

column_map = {
    "sample_id": "sample_id",
    "role": "role",
    "concentration": "concentration",
    "replicate_id": "replicate_id",
    "signal": "signal"
}

def load_assay_csv(filepath): #Load the CSV and print values using logical column names."""
    with open(filepath, newline = "", encoding = "latin-1") as f:
        reader = csv.DictReader(f) #csv.DictReader() is an iterator. Reads the first columm as the header and creates dictionaries of subsequent rows associated with that header. 
        #print(reader.fieldnames)
        calibration_rows = []
        unknown_rows = []
        calibration_groups = {}
        unknown_groups = {}

        for row in reader: # <-- pulling values of the row dictionary and turning them into usable python types.
            
            # parse sample_id, role, concentration, signal
            # append to calibration_rows or unknown_rows
            # build calibration_groups[sample_id]
            # set concentration
            # append signal into the list
            sample_id = row[column_map["sample_id"]]
            role = row[column_map["role"]]
            concentration_str = row[column_map["concentration"]]
            rep_id = row[column_map["replicate_id"]]
            if concentration_str != "":
                concentration = float(concentration_str)
            else:
                concentration = None
            signal_str = row[column_map["signal"]]
            if signal_str != "":
                signal = float(signal_str)
            if role == "CAL":
                calibration_rows.append(row)
                
                if sample_id not in calibration_groups:
                    calibration_groups[sample_id] = {"concentration": None, "signals": []}
                calibration_groups[sample_id]["concentration"] = concentration
                calibration_groups[sample_id]["signals"].append(signal)
            
            elif role == "UNK": 
                unknown_rows.append(row)
                if sample_id not in unknown_groups:
                    unknown_groups[sample_id] = {"signals": []}
                unknown_groups[sample_id]["signals"].append(signal)

            else:
                signal = None

    concentration_means = {} # stored sample concentration float and signal average

    for sample_id, info in calibration_groups.items(): # --> {0.1: 150.6, 0.5: 431.3, 1.0: 697.6, 5.0: 1022.3}
        concentration = info["concentration"]
        signals = info ["signals"]
        final_mean = sum(signals) / len(signals)
        concentration_means[concentration] = final_mean
        
    x_axis = []
    y_axis= []
    for k, v in concentration_means.items():
        x_axis.append(k)
        y_axis.append(v)
    
    pairs = [(x_axis[i], y_axis[i]) for i in range(len(x_axis))]
    pairs.sort()

    x_axis = [p[0] for p in pairs]
    y_axis = [p[1] for p in pairs]
    #print("Unknown groups", unknown_groups)


    return x_axis, y_axis , unknown_groups, calibration_groups


    
if __name__ == "__main__":
    filepath = "/Users/robertboyle/Desktop/Python/Projects/4P_Tool/assets/sample_data/Assay_dataset_2.csv"
    result = load_assay_csv(filepath)
    print(result)



