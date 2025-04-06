import re
from encryption import decrypt
MAX_X_OR_Z = 30_000_000
MAX_Y = 320
MIN_Y = -64

def isCorrectLength(name: str) -> str | bool:
    return True if len(name) <= 30 else "Invalid name length. Must be <= 30 characters."

# Checks for coord format and bounds of the coords sent
def isCorrectCoordFormat(coordinates: str) -> str | bool:
    print(coordinates)
    match = re.fullmatch(r"\s*(-?\d+)\s*[,\s]+\s*(-?\d+)\s*[,\s]+\s*(-?\d+)\s*", coordinates)
    print(match)
    if not match:
        return "Incorrect format. Use double quotes around your coordinates in the form 'X Y Z' or 'X,Y,Z'."
    try:
        x_coord, y_coord, z_coord = map(int, match.groups())
        if not (-MAX_X_OR_Z <= x_coord <= MAX_X_OR_Z):
            return f"X coordinate doesn't fit the bounds allowed within Minecraft...{-MAX_X_OR_Z} to {MAX_X_OR_Z}."
        if not (MIN_Y <= y_coord <= MAX_Y):
            return f"Y coordinate doesn't fit the bounds allowed within Minecraft...{MIN_Y} to {MAX_Y}."
        if not (-MAX_X_OR_Z <= z_coord <= MAX_X_OR_Z):
            return f"Z coordinate doesn't fit the bounds allowed within Minecraft...{-MAX_X_OR_Z} to {MAX_X_OR_Z}."
    except ValueError:
        return "Coordinates are not valid integers(can't be decimals like '10.5' for example)."
    return True


def extract_decrypted_locations(encryptedData):
    decryptedLocations = []
    for entry in encryptedData:
        try:
            decryptedLocations.append({
                'Location_Name': decrypt(entry['Location_Name']).decode(),
                'Coordinates': decrypt(entry['Coordinates']).decode()
            })
        except Exception as e:
            print(f"Error decrypting an item: {e}")
    print(decryptedLocations)
    return decryptedLocations