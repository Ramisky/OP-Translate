#!/usr/bin/env python3
from enum import Enum
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
CARDLIST_DIR = SCRIPT_DIR / "Cardlist"

# Enum class for Release Types
class Release(Enum):
    EB = "EB"
    OP = "OP"
    PRB = "PRB"
    ST = "ST"

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
def grabReleaseNumber(release: Release, releaseNumbers: list[str]) -> str:
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
def grabReleaseCard(release: Release, releaseCards: list[str]) -> str:
    while (user_input := input("Enter Card Number " + releaseCards[0] + " -> " + releaseCards[-1] + ": " ).strip().upper()) not in releaseCards:
        print("Invalid choice!")
    print(f"You successfully selected: {user_input}")
    return user_input

def main():
    release = selectReleaseType()
    releaseNumbers = grabReleaseNumbers(release)
    releaseNumber = grabReleaseNumber(release, releaseNumbers)
    releaseCards = grabReleaseCards(release, releaseNumber)
    releaseCard = grabReleaseCard(release, releaseCards)

    print(release.name + releaseNumber + "-" + releaseCard)

if __name__ == "__main__":
    main()