# address_validation.py
import csv
import requests
import json
from tqdm import tqdm
import config

# Constants
API_KEY = config.API_KEY
API_URL = 'https://addressvalidation.googleapis.com/v1:validateAddress?key=' + API_KEY
INPUT_CSV_PATH = 'fsa_manitoba_errors.csv'
OUTPUT_CSV_PATH = 'CORRECTED_addresses_fsa_manitoba.csv'

def parse_address(row):
    return row['formattedAddress']

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
        fieldnames = ['confirmationNo', 'inputAddress', 'verdict', 'latitude', 'longitude', 'formattedAddress', 'postalCode', 'correctFSA']
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
                'correctFSA': row['New FSA']
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