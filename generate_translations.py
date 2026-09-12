#!/usr/bin/env python3

from enum import Enum
from pathlib import Path

import os
import shutil
import tempfile
import urllib.request

SCRIPT_DIR = Path(__file__).resolve().parent
CARDLIST_DIR = SCRIPT_DIR / "Cardlist"
IMAGE_URL_PREFIX = "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/one-piece/"

# Enum class for Release Types
class Release(Enum):
    EB = "EB"
    OP = "OP"
    PRB = "PRB"
    ST = "ST"

def createTempFolder() -> str:
    # Create the temporary directory
    tmpdir = tempfile.mkdtemp()
    print(f"Created temporary directory at: {tmpdir}")
    return tmpdir

def deleteTempFolder(tmpdir: str):
    shutil.rmtree(tmpdir)
    print("Manually cleaned up the temporary directory.")

# Function for letting the user pick the Release type, resolves to the Enum
def selectReleaseType() -> Release:
    while (user_input := input("Enter 'EB', 'OP', 'PRB', or 'ST': ").strip().upper()) not in ('EB', 'OP', 'PRB', 'ST'):
        print("Invalid choice!")
    print(f"You successfully selected: {user_input}")
    return Release[user_input]

# Function for fetching all the release numbers under the type selected
def grabReleaseNumbers(release: Release) -> list[str]:
    target_path = CARDLIST_DIR / release.name
    releaseNumbers = [x.name for x in target_path.iterdir() if x.is_dir()]
    releaseNumbers.sort()
    return releaseNumbers

# function for letting user choose which release number to select from
def grabReleaseNumber(releaseNumbers: list[str]) -> str:
    while (user_input := input("Enter Release Number " + releaseNumbers[0] + " -> " + releaseNumbers[-1] + ": " ).strip().upper()) not in releaseNumbers:
        print("Invalid choice!")
    print(f"You successfully selected: {user_input}")
    return user_input

# Function for fetching all the card numbers under the release number selected
def grabReleaseCards(release: Release, releaseNumber: str) -> list[str]:
    target_path = CARDLIST_DIR / release.name / releaseNumber
    releaseCards = [file.stem for file in target_path.glob("*.json")]
    releaseCards.sort()
    return releaseCards

# function for letting user choose which card number to select from
def grabReleaseCard(releaseCards: list[str]) -> str:
    while (user_input := input("Enter Card Number " + releaseCards[0] + " -> " + releaseCards[-1] + ": " ).strip().upper()) not in releaseCards:
        print("Invalid choice!")
    print(f"You successfully selected: {user_input}")
    return user_input

# function to combine the image URL
def formImageURL(releaseType: Release, releaseNumber: str, releaseCard: str) -> str:
    release = releaseType.name + releaseNumber
    fullCardNumber = release + "-" + releaseCard
    imageURL = IMAGE_URL_PREFIX + release + "/" + fullCardNumber + "_EN.webp"
    return imageURL

# function to download the card image to our temp folder
def downloadImage(imageURL: str, tmpdir: str):
    file_name = os.path.basename(imageURL)
    full_path = os.path.join(tmpdir, file_name)
    urllib.request.urlretrieve(imageURL, full_path)

def main(tmpdir: str):
    releaseType = selectReleaseType()
    releaseNumbers = grabReleaseNumbers(releaseType)
    releaseNumber = grabReleaseNumber(releaseNumbers)
    releaseCards = grabReleaseCards(releaseType, releaseNumber)
    releaseCard = grabReleaseCard(releaseCards)
    imageURL = formImageURL(releaseType, releaseNumber, releaseCard)
    downloadImage(imageURL, tmpdir)

    print(releaseType.name + releaseNumber + "-" + releaseCard)
    print(imageURL)

if __name__ == "__main__":
    tmpdir = createTempFolder()

    try:
        while True:
            main(tmpdir)  # The temp folder persists across these runs
            
            user_choice = input("\nDo you want to add another card? (y/n): ").strip().lower()
            if user_choice not in ('y', 'yes'):
                break
                
    finally:
        # 2. This guarantees cleanup happens exactly once, 
        # when the user exits or if the program crashes/stops unexpectedly.
        deleteTempFolder(tmpdir)
        print("Goodbye!")