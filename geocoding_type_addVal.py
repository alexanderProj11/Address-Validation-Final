import csv
import requests
from tqdm import tqdm
import config

# Constants
API_KEY = config.API_KEY
GEOCODE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
INPUT_CSV_PATH = 'fsa_manitoba_errors.csv'
OUTPUT_CSV_PATH = 'geocoded_validated_addresses.csv'

def geocode_address(latitude, longitude):
    params = {
        'latlng': f"{latitude},{longitude}",
        'key': API_KEY
    }
    response = requests.get(GEOCODE_API_URL, params=params)
    data = response.json()
    if data['status'] == 'OK':
        # Extract formatted address and postal code
        formatted_address = data['results'][0]['formatted_address']
        postal_code = ''
        for component in data['results'][0]['address_components']:
            if 'postal_code' in component['types']:
                postal_code = component['long_name']
                break
        return formatted_address, postal_code
    else:
        return None, None

def process_csv(reader, total_rows):
    with open(OUTPUT_CSV_PATH, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['confirmationNo', 'Latitude', 'Longitude', 'formattedAddress', 'postalCode', 'correctFSA']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Setup tqdm progress bar
        progress_bar = tqdm(reader, total=total_rows, desc='Geocoding Addresses', unit='rows')
        
        for row in progress_bar:
            latitude = row['Latitude']
            longitude = row['Longitude']
            formatted_address, postal_code = geocode_address(latitude, longitude)

            if formatted_address is not None:
                writer.writerow({
                    'confirmationNo': row['confirmationNo'],
                    'Latitude': latitude,
                    'Longitude': longitude,
                    'formattedAddress': formatted_address,
                    'postalCode': postal_code,
                    'correctFSA': row['New FSA']
                })
            else:
                # Handle cases where geocoding fails
                print(f"Geocoding failed for {row['confirmationNo']}")

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
