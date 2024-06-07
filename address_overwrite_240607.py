import pandas as pd

# Step 1: Open both CSV files
smaller_csv = pd.read_csv("foolproofed_fsa_notifs_240607_1217pm.csv")
larger_csv = pd.read_csv("all_Valid_Addresses_3.csv")

# Step 2: Iterate over each value in the smaller CSV's "confirmationNo" column
for index, row in smaller_csv.iterrows():
    confirmation_no = row["confirmationNo"]
    
    # Step 2.1: Check for matching value in the larger CSV's "confirmationNo" column
    match_row = larger_csv[larger_csv["confirmationNo"] == confirmation_no]
    
    # Step 3: Overwrite fields in the larger CSV with the ones from the smaller CSV
    if not match_row.empty:
        match_index = match_row.index[0]
        larger_csv.loc[match_index, ["Latitude", "Longitude", "formattedAddress", "postalCode", "Forward_Sortation_Area"]] = \
            row[["Latitude", "Longitude", "formattedAddress", "postalCode", "Forward_Sortation_Area"]]

# Save the updated larger CSV
larger_csv.to_csv("valid_addresses_FINALIZED_240607.csv", index=False)
