from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import load_only, joinedload

from app.deps.db import get_async_session
from app.models.track import Track
from app.models.release import Release

router = APIRouter()


@router.get("/mixtape/tracks/matching")
async def find_matching_tracks(
  key: str = None,
  style: str = None,
  bpm: str = None,
  session: AsyncSession = Depends(get_async_session),
):
  # Define a function to find compatible keys based on the Mixed In Key Harmonic Mixing guide
  def get_compatible_keys(key):
    # Extract the key number and type (A for major, B for minor)
    key_number = int(key[:-1])
    key_type = key[-1]

    # Calculate compatible key numbers (with wraparound)
    prev_key_number = 12 if key_number == 1 else key_number - 1
    next_key_number = 1 if key_number == 12 else key_number + 1

    # Determine compatible keys including major/minor switch
    if key_type.upper() == "A":  # Major key
      compatible_keys = [
        f"{key_number}A",
        f"{prev_key_number}A",
        f"{next_key_number}A",
        f"{key_number}B",
      ]
    elif key_type.upper() == "B":  # Minor key
      compatible_keys = [
        f"{key_number}B",
        f"{prev_key_number}B",
        f"{next_key_number}B",
        f"{key_number}A",
      ]
    else:
      compatible_keys = []

    return compatible_keys

  if key and bpm:
    compatible_keys = get_compatible_keys(key)
    if style:
      stmt = select(Track).where((Track.key.in_(compatible_keys)) & (Track.bpm == int(bpm)) & (Track.genre.contains(style)))
      matched_by = "compatible keys, bpm, and genre"
    else:
      stmt = select(Track).where((Track.key.in_(compatible_keys)) & (Track.bpm == int(bpm)))
      matched_by = "compatible keys and bpm"
  elif style:
    stmt = select(Track).where(Track.genre.contains(style))
    matched_by = "genre"
  else:
    matched_by = "none"
    return {"matched_by": matched_by, "matches": 0, "tracks": []}

  stmt = stmt.options(
    load_only(
      Track.name,
      Track.side,
      Track.length,
      Track.rating,
      Track.genre,
      Track.bpm,
      Track.key,
    ),
    joinedload(Track.release).load_only(Release.id_number, Release.thumb),
  )
  result = await session.execute(stmt)
  tracks = result.scalars().all()

  return {"matched_by": matched_by, "matches": len(tracks), "tracks": tracks}
