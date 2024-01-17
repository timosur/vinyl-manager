import discogs_client
from discogs_client.models import Release

from app.core.config import settings

d_client = discogs_client.Client(
  "VinylManager/0.2", user_token=settings.DISCOGS_USER_TOKEN
)

# Types


class DiscogsRelease:
  id: int
  artists: list
  title: str
  labels: list
  thumb: str
  year: int
  genres: list
  styles: list
  catno: str
  format: list
  tracklist: list


# Helper


def _map_artists(raw_artists):
  artists = []

  for artist in raw_artists:
    artists.append(artist.name)

  return artists


def _map_labels(raw_labels):
  labels = []

  for label in raw_labels:
    label_name = label.data.get("name")
    # check if label is already in list
    if label_name not in labels:
      labels.append(label_name)

  return labels


def _map_tracklist(raw_tracklist):
  tracklist = []

  # Process each track in the tracklist
  for track in raw_tracklist:
    # Get the track data
    track = track.data

    # Check if the track has a 'duration' field and it contains ':'
    if "duration" in track and ":" in track["duration"]:
      # Split the duration into minutes and seconds
      minutes, seconds = track["duration"].split(":")
      # Update the duration to be the total in seconds
      track["duration"] = int(minutes) * 60 + int(seconds)
    else:
      # If no duration or format is incorrect, set duration to 0
      track["duration"] = 0

    # drop extraarists and type_ fields
    track.pop("extraartists", None)
    track.pop("type_", None)

    tracklist.append(track)

  return tracklist


# Service functions


def discogs_search(query, page=0):
  results = d_client.search(query).page(page)

  return results


def discogs_search_release(query) -> DiscogsRelease:
  results = d_client.search(query, type="release").page(0)

  if len(results) == 0:
    return None

  release_id = results[0].data.get("id")

  return discogs_map_release(d_client.release(release_id))


def discogs_get_release(release):
  return d_client.release(release)


def discogs_map_release(release: Release) -> DiscogsRelease:
  # Merge the name of all artists into a single string
  artists = _map_artists(release.artists)

  # Get the label name
  labels = _map_labels(release.labels)

  # Get the tracklist
  tracklist = _map_tracklist(release.tracklist)

  # Map genres to a comma-separated string
  genres = ", ".join(release.genres) if release.genres else None

  # Map styles to a comma-separated string
  styles = ", ".join(release.styles) if release.styles else None

  # Map formats names to a comma-separated string
  formats = ", ".join([format["name"] for format in release.formats])

  # Map labels to a comma-separated string
  all_labels = ", ".join(labels) if labels else None

  # Update the release with the new data
  return {
    "id": release.id,
    "artists": artists,
    "title": release.title,
    "labels": labels,
    "all_labels": all_labels,
    "thumb": release.thumb,
    "year": str(release.year),
    "genres": genres,
    "styles": styles,
    "format": formats,
    "tracklist": tracklist,
    "catno": release.labels[0].data.get("catno") if len(release.labels) > 0 else None,
  }


def discogs_get_user_collection(username: str) -> list[DiscogsRelease]:
  collection = d_client.user(username).collection_folders[0].releases

  # Process each release in the collection
  releases = []

  for raw_release in collection:
    # Get the release data
    raw_release = raw_release.data

    # Get the whole release data
    release = d_client.release(raw_release["id"])

    releases.append(discogs_map_release(release))

  return releases
