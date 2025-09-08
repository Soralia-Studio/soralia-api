from typing import List

from fastapi import APIRouter, HTTPException, Query

from src.models import (
    Difficulty,
    SheetType,
    SongResponse,
    SongSearchParams,
    SongsListResponse,
)
from src.services.songs import songs_service

__all__ = ["router"]

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/", response_model=SongsListResponse)
async def get_songs(
    skip: int = Query(default=0, ge=0, description="Number of songs to skip"),
    limit: int = Query(
        default=100, le=1000, ge=1, description="Number of songs to return"
    ),
):
    """Get all songs with pagination"""
    songs, total = songs_service.get_all_songs(skip=skip, limit=limit)
    return SongsListResponse(songs=songs, total=total)


@router.get("/{song_id}", response_model=SongResponse)
async def get_song(song_id: str):
    """Get a specific song by its ID"""
    song = songs_service.get_song_by_id(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.get("/search/", response_model=SongsListResponse)
async def search_songs(
    title: str = Query(default=None, description="Search in song title"),
    artist: str = Query(default=None, description="Search in artist name"),
    category: str = Query(default=None, description="Search in category"),
    version: str = Query(default=None, description="Search in game version"),
    difficulty: Difficulty = Query(default=None, description="Filter by difficulty"),
    sheet_type: SheetType = Query(
        default=None, description="Filter by sheet type (dx/std)"
    ),
    level_min: float = Query(default=None, ge=1, le=15, description="Minimum level"),
    level_max: float = Query(default=None, ge=1, le=15, description="Maximum level"),
    bpm_min: int = Query(default=None, ge=1, description="Minimum BPM"),
    bpm_max: int = Query(default=None, ge=1, description="Maximum BPM"),
    is_new: bool = Query(default=None, description="Filter by new songs"),
    is_locked: bool = Query(default=None, description="Filter by locked songs"),
    skip: int = Query(default=0, ge=0, description="Number of songs to skip"),
    limit: int = Query(
        default=100, le=1000, ge=1, description="Number of songs to return"
    ),
):
    """Search songs with various filters"""
    search_params = SongSearchParams(
        title=title,
        artist=artist,
        category=category,
        version=version,
        difficulty=difficulty,
        sheet_type=sheet_type,
        level_min=level_min,
        level_max=level_max,
        bpm_min=bpm_min,
        bpm_max=bpm_max,
        is_new=is_new,
        is_locked=is_locked,
        skip=skip,
        limit=limit,
    )

    songs, total = songs_service.search_songs(search_params)
    return SongsListResponse(songs=songs, total=total)


@router.get("/metadata/categories", response_model=List[str])
async def get_categories():
    """Get all available song categories"""
    return songs_service.get_categories()


@router.get("/metadata/versions", response_model=List[str])
async def get_versions():
    """Get all available game versions"""
    return songs_service.get_versions()


@router.get("/metadata/artists", response_model=List[str])
async def get_artists():
    """Get all available artists"""
    return songs_service.get_artists()


@router.get("/stats/summary")
async def get_stats():
    """Get summary statistics about the song database"""
    songs, total = songs_service.get_all_songs(limit=999999)  # Get all songs

    categories = songs_service.get_categories()
    versions = songs_service.get_versions()
    artists = songs_service.get_artists()

    # Calculate some basic stats
    total_sheets = sum(len(song.sheets) for song in songs)
    avg_bpm = sum(song.bpm for song in songs) / len(songs) if songs else 0
    new_songs = sum(1 for song in songs if song.is_new)
    locked_songs = sum(1 for song in songs if song.is_locked)

    return {
        "total_songs": total,
        "total_sheets": total_sheets,
        "total_categories": len(categories),
        "total_versions": len(versions),
        "total_artists": len(artists),
        "average_bpm": round(avg_bpm, 1),
        "new_songs": new_songs,
        "locked_songs": locked_songs,
    }
