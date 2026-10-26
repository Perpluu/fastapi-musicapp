from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class ArtistBase(BaseModel):
    name: str
    bio: Optional[str] = ""
    country: Optional[str] = "Unknown"
    avatar_url: Optional[str] = "https://via.placeholder.com/80"


class ArtistCreate(ArtistBase):
    pass


class ArtistUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    country: Optional[str] = None
    avatar_url: Optional[str] = None


class ArtistResponse(ArtistBase):
    id: int

    class Config:
        from_attributes = True


class SongBase(BaseModel):
    title: str
    genre: str
    album: Optional[str] = "Single"
    duration_sec: int = Field(default=180, gt=0)
    youtube_url: str
    artist_id: int


class SongCreate(SongBase):
    pass


class SongUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    album: Optional[str] = None
    duration_sec: Optional[int] = None
    youtube_url: Optional[str] = None
    artist_id: Optional[int] = None


class SongResponse(SongBase):
    id: int
    plays_count: int
    artist: Optional[ArtistResponse] = None
    recommended_score: Optional[int] = 0  # Wypełniane dynamicznie na podstawie ciasteczka music_taste

    class Config:
        from_attributes = True


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = ""


class PlaylistCreate(PlaylistBase):
    song_ids: Optional[List[int]] = []


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    song_ids: Optional[List[int]] = None


class PlaylistResponse(PlaylistBase):
    id: int
    owner_id: int
    songs: List[SongResponse] = []

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=2)
    song_id: int


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True