#!/usr/bin/env python3

import requests
import json
import os
import re

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CARDLIST_DIR = SCRIPT_DIR / "Cardlist"
URL_STEM = 'https://optcgapi.com/api/allSets/'
URL_CARD_STEM = 'https://optcgapi.com/api/sets/'
ST_URL_STEM = 'https://optcgapi.com/api/allDecks/'
ST_CARD_STEM = 'https://optcgapi.com/api/decks/'
P_URL_STEM = 'https://www.optcgapi.com/api/allPromos/'
RELEASES = ('EB', 'OP', 'P', 'PRB', 'ST')

def safe_split(text, separator):
    if (separator in text and separator != ''):
        return text.split(separator, 1)
    elif ('-' in text):
        return text.split('-', 1)
    else:
        return text

def get_values_by_key(data, target_key):
    """
    Recursively searches for a specific key in a JSON-like structure 
    and returns a list of all matching values.
    """
    results = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                results.append(value)
            # Recursively search through inner dictionaries or lists
            results.extend(get_values_by_key(value, target_key))
            
    elif isinstance(data, list):
        for item in data:
            # Recursively search through items inside the list
            results.extend(get_values_by_key(item, target_key))
            
    return results

def createSetFolders():
    for release in RELEASES:
        folder_path = CARDLIST_DIR / release
        folder_path.mkdir(parents=True, exist_ok=True)

def grabReleaseTypes() -> list[str]:
    target_path = CARDLIST_DIR
    releases = [x.name for x in target_path.iterdir() if x.is_dir()]
    releases.sort()
    return releases

def createSets(releaseTypes: list[str]):

    for releaseType in releaseTypes:
        releaseNumbers = []
        try:
            if (releaseType == 'ST'):
                response = requests.get(ST_URL_STEM)
            elif (releaseType == 'P'):
                continue
            else:
                response = requests.get(URL_STEM)
            response_text = response.json()

            if (releaseType == 'ST'):
                releaseNumbers = get_values_by_key(response_text, 'structure_deck_id')
            elif (releaseType == 'P'):
                continue
            else:
                releaseNumbers = get_values_by_key(response_text, 'set_id')

            if (releaseType == 'P'):
                continue
                '''for releaseNumber in releaseNumbers:
                    with open(json_path, 'w', encoding='utf-8') as file:
                        json.dump(json_data, file, indent=4)'''
            else:
                for releaseNumber in releaseNumbers:
                        cutReleaseNumber = ''
                        cutReleaseType = releaseNumber.split('-', 1)[0]

                        if (cutReleaseType == releaseType):
                            cutReleaseNumber = releaseNumber.split('-', 1)[1]
                            if 'EB' in cutReleaseNumber:
                                print('Skipping Processing: ' + str(releaseNumber))
                                continue
                            else:
                                print('Processing: ' + str(releaseNumber))
                                cutReleaseNumber = releaseNumber.split('-', 1)[1]
                                path = CARDLIST_DIR / releaseType / cutReleaseNumber
                                path.mkdir(parents=True, exist_ok=True)

                        if ('EB' in releaseNumber.split('-', 1)[1] and releaseType == 'OP'):
                            cutReleaseNumber = releaseNumber.split('-', 1)[0].replace("OP", "")
                            path = CARDLIST_DIR / releaseType / cutReleaseNumber
                            path.mkdir(parents=True, exist_ok=True)
                            print('Skipping? Processing: ' + str(releaseNumber))

                        if ('EB' in releaseNumber.split('-', 1)[1] and releaseType == 'EB'):
                            try:
                                print('Finally Processing: ' + str(releaseNumber))
                                cutReleaseNumber = releaseNumber.split('EB', 1)[1]
                                path = CARDLIST_DIR / releaseType / cutReleaseNumber
                                path.mkdir(parents=True, exist_ok=True)
                            except IndexError:
                                print("Oops! The string did not split into enough parts.")

        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"Error reading: {e}")

def grabReleases(releaseType: str) -> list[str]:
    target_path = CARDLIST_DIR / releaseType
    releases = [x.name for x in target_path.iterdir() if x.is_dir()]
    releases.sort()
    return releases

def createCards(cardNumbers: list, releaseType: str):
        for cardNumber in cardNumbers:
            if ('EB04' in cardNumber):
                print(cardNumber)
                # OP16-001 -> 16-001
                cutCardId = re.sub(r"[^0-9-]", "", cardNumber)
                # 16-001 -> 16
                releaseNumber = '04'
                # OP16-001 -> OP
                cutReleaseType = 'EB'
                # 16-001 -> 001
                cardNumber = cutCardId.split('-', 1)[1]
                path = CARDLIST_DIR / cutReleaseType / releaseNumber
                fileName = cardNumber + '.json'
                fullPath = path / fileName
                with open(fullPath, "a") as f:
                    pass  
            else:
                print(cardNumber)
                # OP16-001 -> 16-001
                cutCardId = re.sub(r"[^0-9-]", "", cardNumber)
                # 16-001 -> 16
                releaseNumber = cutCardId.split('-', 1)[0]
                # OP16-001 -> OP
                cutReleaseType = re.sub(r"[^a-zA-Z]", "", cardNumber)
                if (releaseType == cutReleaseType):
                    # 16-001 -> 001
                    cardNumber = cutCardId.split('-', 1)[1]
                    path = CARDLIST_DIR / cutReleaseType / releaseNumber
                    fileName = cardNumber + '.json'
                    fullPath = path / fileName
                    with open(fullPath, "a") as f:
                        pass
                else:
                    print('release type above not equal to card release type')
                    print('release type: ' + releaseType)
                    print('card release no.: ' + releaseNumber)
                    print('card release type: ' + cutReleaseType)

def fetchCards(releaseTypes: str):
    url = ''
    cardNumbers = []
    for releaseType in releaseTypes:
        if (releaseType == 'P'):
            url = P_URL_STEM
            result = requests.get(url)
            response_text = result.json()
            cardNumbers = get_values_by_key(response_text, 'card_set_id')
            createCards(cardNumbers, releaseType)
        elif (releaseType == 'ST'):
            releases = grabReleases(releaseType)
            for release in releases:
                fullRelease = releaseType + "-" + release + '/'
                url = ST_CARD_STEM + fullRelease
                result = requests.get(url)
                response_text = result.json()
                cardNumbers = get_values_by_key(response_text, 'card_set_id')
                createCards(cardNumbers, releaseType)
        else:
            releases = grabReleases(releaseType)
            for release in releases:
                    if (release != '14' and release != '15'):
                        fullRelease = releaseType + "-" + release + '/'
                        url = URL_CARD_STEM + fullRelease
                        result = requests.get(url)
                        response_text = result.json()
                        cardNumbers = get_values_by_key(response_text, 'card_set_id')
                        createCards(cardNumbers, releaseType)
                    else:
                        fullRelease = releaseType + release + "-EB04"
                        url = URL_CARD_STEM + fullRelease
                        result = requests.get(url)
                        response_text = result.json()
                        cardNumbers = get_values_by_key(response_text, 'card_set_id')
                        createCards(cardNumbers, releaseType)
        
def main():
    createSetFolders()
    releaseTypes = grabReleaseTypes()
    createSets(releaseTypes)
    fetchCards(releaseTypes)

if __name__ == "__main__":
    main()