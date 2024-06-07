# address_validation.py
import csv
import requests
import json
from tqdm import tqdm
import config

# Constants
API_KEY = config.API_KEY
API_URL = 'https://addressvalidation.googleapis.com/v1:validateAddress?key=' + API_KEY
INPUT_CSV_PATH = '/home/salaalex382/CSV Files/Addr_Train_MK3.csv'
OUTPUT_CSV_PATH = '/home/salaalex382/CSV Files/addresses_output_mk3.csv'

def parse_address(row):
    return f"{row['Address']}, {row['City']}, {row['Province']}, {row['Postal Code']}, {row['Country']}"

def validate_address(address):
    headers = {'Content-Type': 'application/json'}
    body = {'address': {'addressLines': [address]}}
    response = requests.post(API_URL, headers=headers, json=body)
    return response.json()

def format_verdict(verdict_info):
    # Extract and format the verdict details from the API response
    input_granularity = verdict_info.get('inputGranularity', 'N/A')
    validation_granularity = verdict_info.get('validationGranularity', 'N/A')
    has_replaced_components = 'Yes' if verdict_info.get('hasReplacedComponents', False) else 'No'
    has_inferred_components = 'Yes' if verdict_info.get('hasInferredComponents', False) else 'No'
    return f"Input Granularity: {input_granularity}, Validation Granularity: {validation_granularity}, Replaced Components: {has_replaced_components}, Inferred Components: {has_inferred_components}"

def process_csv(reader, total_rows):
    with open(OUTPUT_CSV_PATH, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['confirmationNo', 'inputAddress', 'verdict', 'latitude', 'longitude', 'formattedAddress', 'postalCode', 'errorMessage', 'supportDescription', 'riskType', 'submittedDate', 'startDate', 'endDate', 'owner', 'ownerPhoneNumber', 'contractor', 'siteContact', 'contactPhoneNumber', 'compName', 'compPhoneNumber']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Setup tqdm progress bar
        progress_bar = tqdm(reader, total=total_rows, desc='Validating Addresses', unit='rows')
        
        for row in progress_bar:
            full_address = parse_address(row)
            validation_result = validate_address(full_address)
            result = validation_result.get('result', {})
            geocode = result.get('geocode', {})
            location = geocode.get('location', {})
            verdict_info = result['verdict']

            # Print a message for each processed row
            print(f"Validated {row['confirmationNo']}")

            writer.writerow({
                'confirmationNo': row['confirmationNo'],
                'inputAddress': full_address,
                'verdict': format_verdict(verdict_info),
                'latitude': location.get('latitude', ''),
                'longitude': location.get('longitude', ''),
                'formattedAddress': result.get('address', {}).get('formattedAddress', ''),
                'postalCode': result.get('address', {}).get('postalAddress', {}).get('postalCode', ''),
                'errorMessage': validation_result.get('error', {}).get('message', 'No error'),
                'supportDescription': row['supportDescription'],
                'riskType': row['riskType'],
                'submittedDate': row['submittedDate'],
                'startDate': row['startDate'],
                'endDate': row['endDate'],
                'owner': row['owner'],
                'ownerPhoneNumber': row['ownerPhoneNumber'],
                'contractor': row['contractor'],
                'siteContact': row['siteContact'],
                'contactPhoneNumber': row['contactPhoneNumber'],
                'compName': row['compName'],
                'compPhoneNumber': row['compPhoneNumber']
            })

def process_addresses():
    encodings = ['utf-8', 'latin1', 'windows-1252']
    for encoding in encodings:
        try:
            with open(INPUT_CSV_PATH, mode='r', newline='', encoding=encoding) as file:
                reader = csv.DictReader(file)
                # Get total rows for the progress bar (by converting reader to a list)
                rows = list(reader)
                total_rows = len(rows)
                process_csv(rows, total_rows)
            break
        except UnicodeDecodeError:
            continue

if __name__ == "__main__":
    process_addresses()