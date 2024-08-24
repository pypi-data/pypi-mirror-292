import pandas as pd
import os
import json


import pandas as pd
import os
import json
import csv

def json_to_csv(start, end, prefix, output_csv, data_dir="data", overwrite=False):
    """
    Convert JSON files to a single CSV file with each JSON file represented as a row.
    """
    # Create the output CSV file path if not provided
    if output_csv == "":
        output_csv = f"{prefix}_{start}-{end}.csv"
    if os.path.exists(output_csv) and not overwrite:
        return
    elif os.path.exists(output_csv) and overwrite:
        os.remove(output_csv)
    
    # Define the field names for the CSV file
    fieldnames = ["HologramID", "SignedBy", "productDescription", "Inscription", "LimitedEdition", "valid"]
    
    # Open the CSV file for writing
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Write the header row

        flag = False

        for i in range(start, end):
            json_file = os.path.join(data_dir, f"{prefix}{str(i).zfill(6)}.json")

            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    data = json.load(f)

                    # Normalize JSON data if needed
                    athletes = data.get("athletes", [])
                    if athletes is None:
                        athletes = []
                    normalized_data = {
                        "HologramID": f"{prefix}{str(i).zfill(6)}",
                        "SignedBy": "，".join(athletes),
                        "productDescription": data.get("productDescription", "").replace(",", "，"),
                        "Inscription": data.get("Inscription", "").replace(",", "，"),
                        "LimitedEdition": data.get("LE", "").replace(",", "，"),
                        "valid": data.get("valid", "")
                    }

                    # Write the normalized data to the CSV file
                    writer.writerow(normalized_data)
            else:
                flag = True
                print(f"Failed to convert {prefix}{str(i).zfill(6)}.json to CSV.")
        
        if flag:
            print("Some JSON files failed to convert to CSV. Please check the output.")
        else:
            print("All JSON files have been converted to CSV successfully.")

def json_to_excel(start, end, prefix, output_excel, data_dir="data"):
    """
    Convert JSON files to Excel with each file represented as a sheet.
    """
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    if(output_excel == ""):
        output_excel = f"{prefix}_{start}-{end}.xlsx"
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        flag = False
        
        for i in range(start, end):
            json_file = os.path.join(data_dir, f"{prefix}{str(i).zfill(6)}.json")
            
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    data = json.load(f)
                    
                    # Normalize JSON data if needed
                    athletes = data.get("athletes", [])
                    if athletes is None:
                        athletes = []
                    normalized_data = {
                        "HologramID": i,
                        "SignedBy": "，".join(athletes),
                        "productDescription": data.get("productDescription", "").replace(",", "，"),
                        "Inscription": data.get("Inscription", "").replace(",", "，"),
                        "LimitedEdition": data.get("LE", "").replace(",", "，"),
                        "valid": data.get("valid", "")
                    }
                    
                    # Create a DataFrame
                    df = pd.DataFrame([normalized_data])
                    
                    # Write the DataFrame to an Excel sheet
                    df.to_excel(writer, sheet_name=f"{i}", index=False)
            else:
                flag = True
                print(f"Failed to convert {i}.json to Excel.")
        
        if flag:
            print("Some JSON files failed to convert to Excel. Please check the output.")
        else:
            print("All JSON files have been converted to Excel successfully.")
