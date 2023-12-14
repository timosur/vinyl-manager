from http.client import HTTPException
from fastapi import APIRouter, HTTPException

from app.service.discogs import discogs_search_tracklist, discogs_get_user_collection, discogs_search

router = APIRouter()

@router.get("/discogs/search")
async def search(query: str = "", page: int = 0):
  return discogs_search(query, page)

@router.get("/discogs/tracklist")
async def tracklist(release: str = ""):
  tracklist = discogs_search_tracklist(release)

  if tracklist is None:
    raise HTTPException(status_code=404, detail="Release not found")

  return tracklist

@router.get("/discogs/collection")
async def collection(username: str = ""):
  return discogs_get_user_collection(username)