from http.client import HTTPException

from fastapi import APIRouter, HTTPException

from app.service.discogs import (
  discogs_get_user_collection,
  discogs_search,
  discogs_search_release,
)

router = APIRouter()


@router.get("/discogs/search")
async def search(query: str = "", page: int = 0):
  return discogs_search(query, page)


@router.get("/discogs/tracklist")
async def tracklist(release: str = ""):
  release = discogs_search_release(release)

  if release is None or release.tracklist is None:
    raise HTTPException(status_code=404, detail="Release not found")

  return release.tracklist


@router.get("/discogs/collection")
async def collection(username: str = ""):
  return discogs_get_user_collection(username)
