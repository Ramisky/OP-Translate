#!/usr/bin/env python3

import requests
import json
import os

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CARDLIST_DIR = SCRIPT_DIR / "Cardlist"
URL_STEM = 'https://optcgapi.com/api/sets/card/'
ST_URL_STEM = 'https://optcgapi.com/api/decks/card/'
P_URL_STEM = 'https://www.optcgapi.com/api/promos/card/'

# Recursively removes a key from nested dictionaries and lists.
def remove_subfield_recursively(data, target_key) -> json:
    if isinstance(data, dict):
        # Remove the key if it exists in the current dictionary layer
        data.pop(target_key, None)
        # Recurse down into the remaining keys
        for key, value in data.items():
            remove_subfield_recursively(value, target_key)
    elif isinstance(data, list):
        # If a list is encountered, check every item inside it
        for item in data:
            remove_subfield_recursively(item, target_key)
    return data
    

def downloadJSONByPath(path: Path) -> json:
    file_name = f"{path.parent.parent.stem}{path.parent.stem}-{path.stem}/"
    URL = os.path.join(URL_STEM, file_name)

    if (path.parent.parent.stem == 'ST'):
        URL = os.path.join(ST_URL_STEM, file_name)

    if (path.parent.stem == 'P'):
        file_name = f"{path.parent.stem}-{path.stem}/"
        URL = os.path.join(P_URL_STEM, file_name)

    response = requests.get(URL)
    response_text = response.json()
    response_text = remove_subfield_recursively(response_text, 'inventory_price')
    response_text = remove_subfield_recursively(response_text, 'market_price')
    return response_text

def iterateOverJSONs():
    for json_path in CARDLIST_DIR.rglob("*.json"):
        try:
            json_data = downloadJSONByPath(json_path)
            print('Printing: ' + str(json_path))
            with open(json_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4)
                #print(json_data)

        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"Error reading {json_path}: {e}")    

def main():
    iterateOverJSONs()

if __name__ == "__main__":
    main()