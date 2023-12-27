from pydantic import BaseModel, UUID4
from typing import List, Optional

class ArtistUpdate(BaseModel):
    id: UUID4
    name: Optional[str]

class LabelUpdate(BaseModel):
    id: UUID4
    name: Optional[str]

class TrackUpdate(BaseModel):
    id: UUID4
    name: Optional[str]
    side: Optional[str]
    length: Optional[int]
    rating: Optional[int]
    genre: Optional[str]
    bpm: Optional[int]
    key: Optional[str]
    audio: Optional[str] = None

    # Add a method to read file content if necessary
    def get_audio_data(self):
        if self.audio:
            return self.audio
        return None

class ReleaseUpdate(BaseModel):
    name: Optional[str]
    short: Optional[str]
    notes: Optional[str]
    labels: Optional[List[LabelUpdate]]
    artists: Optional[List[ArtistUpdate]]
    tracks: Optional[List[TrackUpdate]]

    class Config:
        orm_mode = True
