from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Text
from sqlalchemy.orm import relationship
from app.database import Base

playlist_songs = Table(
    "playlist_songs",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # 'admin', 'moderator', 'user'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="author", cascade="all, delete-orphan")


class Artist(Base):
    """Zasób CRUD #1: Artyści / Wykonawcy"""
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    bio = Column(Text, default="")
    country = Column(String(50), default="Unknown")
    avatar_url = Column(String(255), default="https://via.placeholder.com/80")

    songs = relationship("Song", back_populates="artist", cascade="all, delete-orphan")


class Song(Base):
    """Zasób CRUD #2: Piosenki (wyświetlane jako pionowe 'bary')"""
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), index=True, nullable=False)
    genre = Column(String(50), index=True, nullable=False)  # RNB/SOUL, RNB, RAP, EDM, LATINO
    album = Column(String(120), default="Single")
    duration_sec = Column(Integer, nullable=False, default=180)
    youtube_url = Column(String(255), nullable=False)  # Link do YouTube
    plays_count = Column(Integer, default=0)
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)

    artist = relationship("Artist", back_populates="songs")
    playlists = relationship("Playlist", secondary=playlist_songs, back_populates="songs")
    reviews = relationship("Review", back_populates="song", cascade="all, delete-orphan")


class Playlist(Base):
    """Zasób CRUD #3: Playlisty użytkowników"""
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), default="")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary=playlist_songs, back_populates="playlists")


class Review(Base):
    """Zasób CRUD #4: Recenzje / Komentarze pod utworami"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)  # Ocena 1-5
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)

    author = relationship("User", back_populates="reviews")
    song = relationship("Song", back_populates="reviews")