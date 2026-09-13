#!/usr/bin/env python3

from enum import Enum
from pathlib import Path, PurePosixPath
from PIL import Image
from itertools import batched
from datetime import datetime

import json
import os
import shutil
import tempfile
import urllib.request

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "out"
CARDLIST_DIR = SCRIPT_DIR / "Cardlist"
IMAGE_URL_PREFIX = "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/one-piece/"
IMAGE_START_X = 0
IMAGE_START_Y = 500
IMAGE_END_X = 600
IMAGE_END_Y = 838
DPI_DEFAULT = 240

# Enum class for Release Types
class Release(Enum):
    EB = "EB"
    OP = "OP"
    P = "P"
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
    while (user_input := input("Enter 'EB', 'OP', 'P', 'PRB', or 'ST': ").strip().upper()) not in ('EB', 'OP', 'P', 'PRB', 'ST'):
        print("Invalid choice!")
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
    return user_input

def grabNumberOfCard() -> int:
        while (user_input := input("Enter Number of Card to print 1 -> 4: " ).strip().upper()) not in ('1', '2', '3', '4'):
            print("Invalid choice!")
        return int(user_input)

# function to download the card image to our temp folder
def downloadImage(imageURL: str, tmpdir: str, number: int):
    for i in range(number):
        file_name = os.path.basename(imageURL)
        file_path = Path(file_name)

        stem = file_path.stem  # "document"
        suffix = file_path.suffix  # ".txt"

        file_name = f"{stem}_{i}{suffix}"
        full_path = os.path.join(tmpdir, file_name)
        urllib.request.urlretrieve(imageURL, full_path)
        cropImage(full_path)

def cropImage(imagePath: str):
    with Image.open(imagePath) as img:
        # (left, upper, right, lower)
        cropped_img = img.crop((IMAGE_START_X, IMAGE_START_Y, IMAGE_START_X + IMAGE_END_X, IMAGE_START_Y + IMAGE_END_Y))
        bbox = cropped_img.getbbox()
        if bbox:
            cropped_img = cropped_img.crop(bbox)
        cropped_img.convert('RGB').save(imagePath)

def findDownloadedImages(tempFolder: str) -> list[str]:
    cards = [file for file in Path(tempFolder).glob("*.jpg")]
    cards.sort()
    return cards

def combineImagesToA4(image_paths, dpi=DPI_DEFAULT, cols=3, rows=7):
    # A4 dimensions in pixels at given DPI (Standard A4: 8.27 x 11.69 inches)
    a4_width = int(8.27 * dpi)
    a4_height = int(11.69 * dpi)
    
    # Create white A4 background canvas
    canvas = Image.new("RGB", (a4_width, a4_height), (255, 255, 255))
    
    cell_width = a4_width // cols
    cell_height = a4_height // rows
    
    for index, path in enumerate(image_paths[:cols * rows]):
        img = Image.open(path)
        img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)
        
        # Calculate grid position
        col_idx = index % cols
        row_idx = index // cols
        
        x = col_idx * cell_width + (cell_width - img.width) // 2
        y = row_idx * cell_height + (cell_height - img.height) // 2
        
        canvas.paste(img, (x, y))

    return canvas

def combineA4ToPDF(images, output_pdf_path, dpi=DPI_DEFAULT):
    images[0].save(
        output_pdf_path, 
        "PDF", 
        append_images=images[1:], 
        resolution=dpi
    )

def combineImages(tempFolder: str):
    now = datetime.now()
    # 2. Format it into a safe string (e.g., "20261024-153045")
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    file_name = f"op-tcg-print_{timestamp}.pdf"

    downloadImages = findDownloadedImages(tempFolder)
    combinedImages = []
    batch_size = 21
    OUT_FILE = OUT_DIR / PurePosixPath(file_name)
    for batch in batched(downloadImages, batch_size):
        combinedImages.append(combineImagesToA4(batch))
    combineA4ToPDF(combinedImages, OUT_FILE)

def find_pairs_recursively(data, key1="card_image_id", key2="card_image"):
    results = {}
    
    if isinstance(data, dict):
        # Look for matching target keys at the exact same hierarchy level
        if key1 in data and key2 in data:
            results[data[key1]] = data[key2]
        
        # Keep searching deeper branches
        for value in data.values():
            results.update(find_pairs_recursively(value, key1, key2))
            
    elif isinstance(data, list):
        for item in data:
            results.update(find_pairs_recursively(item, key1, key2))
            
    return results

def grabCardArtPairs(releaseType: str, releaseNumber: str, releaseCard: str):
    jsonName = releaseCard + ".json"
    filename = CARDLIST_DIR / releaseType.name / releaseNumber / jsonName
    try:
        # 1. Safely open the file using a context manager and proper encoding
        with open(filename, "r", encoding="utf-8") as file:
            # 2. Parse the JSON safely
            data = json.load(file)
            return find_pairs_recursively(data)

    except FileNotFoundError:
        print(error=f"The file '{filename}' could not be found.")

    except json.JSONDecodeError as e:
        # 3. Handle malformed or corrupted JSON safely without crashing
        print(f"Invalid JSON format. Error on line {e.lineno}, column {e.colno}: {e.msg}")

def pickCardArtPair(cardArtPairs: dict):
    if (len(cardArtPairs.keys()) > 1):
        print('Pick a Card from the following')
        for i in range(1, len(cardArtPairs.keys()) + 1):
            print (str(i) + ': ' + list(cardArtPairs)[i - 1])
        while (user_input := int(input("Enter Selection: " ).strip().upper())) not in range(1, len(cardArtPairs.keys()) + 1):
            print("Invalid choice!")
        return cardArtPairs.get(list(cardArtPairs)[user_input - 1])
    elif (len(cardArtPairs.keys()) == 1):
        return cardArtPairs.get(list(cardArtPairs)[0])
    else:
        print("No Images Available for Card")
        return ""

def main(tmpdir: str):
    releaseType = selectReleaseType()
    releaseNumbers = grabReleaseNumbers(releaseType)
    releaseNumber = grabReleaseNumber(releaseNumbers)
    releaseCards = grabReleaseCards(releaseType, releaseNumber)
    releaseCard = grabReleaseCard(releaseCards)
    cardArtPairs = grabCardArtPairs(releaseType, releaseNumber, releaseCard)
    imageURL = pickCardArtPair(cardArtPairs)
    if (imageURL != ''):
        numberOfCard = grabNumberOfCard()
        downloadImage(imageURL, tmpdir, numberOfCard)
        print(releaseType.name + releaseNumber + "-" + releaseCard)
  
if __name__ == "__main__":
    tmpdir = createTempFolder()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            main(tmpdir)  # The temp folder persists across these runs
            
            user_choice = input("\nDo you want to add another card? (y/n): ").strip().lower()
            if user_choice not in ('y', 'yes'):
                combineImages(tmpdir)
                break
                
    finally:
        # 2. This guarantees cleanup happens exactly once, 
        # when the user exits or if the program crashes/stops unexpectedly.
        deleteTempFolder(tmpdir)
        print("Goodbye!")