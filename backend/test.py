# Call https://www.deejay.de/ajaxHelper/fp.php?t=item["ID"]&DEEJAY_SHOP=&s=
# Get tracklist from response
import re
import requests


def extract_all_track_titles(track_strings):
    track_details = []
    for track in track_strings:
        # Extracting all occurrences of track name, side, and title using regex
        matches = re.findall(r'~([A-Za-z0-9_+]+)~.*?[ab]~[0-9]~[ab]\\0\\([AB][0-9]) \| ([^~]+)', track)
        for match in matches:
            track_name, side, title = match
            track_details.append({'track_name': track_name, 'side': side, 'title': title})
    return track_details

# Updated example input strings
track_strings = [
    "0171602024~950465~Numilume~4~NUM004~a~0~a\\0\\A1 | Antares~b\\0\\B1 | Resiliency",
    "0171602024~991711~Yaroslav+Kinsky~ALT+EP~SEMDV001~a~0~a\\0\\A1 | Alt~b\\0\\A2 | Enduro~c\\0\\B1 | Moons~d\\0\\B2 | Moons (Pablo Bolivar Remix)"
]

print(extract_all_track_titles(track_strings))
