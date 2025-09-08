import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.models import Song, SongSearchParams


class SongsService:
    def __init__(self):
        self.data_file = Path("data/maimai_song.json")
        self._songs_cache: Optional[List[Song]] = None

    @property
    def song_cache(self) -> List[Song]:
        if self._songs_cache is None:
            self._load_songs()
        return self._songs_cache  # type: ignore

    def _load_songs(self) -> List[Song]:
        if self._songs_cache is None:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._songs_cache = []
            for song_data in data.get("songs", []):
                if song_data.get("releaseDate"):
                    song_data["releaseDate"] = datetime.strptime(
                        song_data["releaseDate"], "%Y-%m-%d"
                    ).date()

                print(song_data)
                song = Song.model_validate(song_data)
                self._songs_cache.append(song)

        return self._songs_cache

    def get_all_songs(self, skip: int = 0, limit: int = 100) -> tuple[List[Song], int]:
        songs = self._load_songs()
        total = len(songs)

        if limit < 1:
            return songs, total

        paginated_songs = songs[skip : skip + limit]
        return paginated_songs, total

    def get_song_by_id(self, song_id: str) -> Optional[Song]:
        songs = self._load_songs()

        for song in songs:
            if song.song_id == song_id:
                return song

        return None

    def search_songs(self, params: SongSearchParams) -> tuple[List[Song], int]:
        songs = self._load_songs()
        filtered_songs = []

        for song in songs:
            if params.title and params.title.lower() not in song.title.lower():
                continue

            if params.artist and params.artist.lower() not in song.artist.lower():
                continue

            if params.category and params.category.lower() not in song.category.lower():
                continue

            if params.version and params.version.lower() not in song.version.lower():
                continue

            if params.bpm_min is not None and song.bpm < params.bpm_min:
                continue

            if params.bpm_max is not None and song.bpm > params.bpm_max:
                continue

            if params.is_new is not None and song.is_new != params.is_new:
                continue

            if params.is_locked is not None and song.is_locked != params.is_locked:
                continue

            if any(
                [
                    params.difficulty,
                    params.level_min,
                    params.level_max,
                    params.sheet_type,
                ]
            ):
                matching_sheet_found = False

                for sheet in song.sheets:
                    sheet_matches = True

                    if params.difficulty and sheet.difficulty != params.difficulty:
                        sheet_matches = False

                    if params.sheet_type and sheet.type != params.sheet_type:
                        sheet_matches = False

                    if (
                        params.level_min is not None
                        and sheet.level_value < params.level_min
                    ):
                        sheet_matches = False

                    if (
                        params.level_max is not None
                        and sheet.level_value > params.level_max
                    ):
                        sheet_matches = False

                    if sheet_matches:
                        matching_sheet_found = True
                        break

                if not matching_sheet_found:
                    continue

            filtered_songs.append(song)

        total = len(filtered_songs)

        paginated_songs = filtered_songs[params.skip : params.skip + params.limit]

        return paginated_songs, total

    def get_categories(self) -> List[str]:
        songs = self._load_songs()
        categories = list(set(song.category for song in songs))
        return sorted(categories)

    def get_versions(self) -> List[str]:
        songs = self._load_songs()
        versions = list(set(song.version for song in songs))
        return sorted(versions)

    def get_artists(self) -> List[str]:
        songs = self._load_songs()
        artists = list(set(song.artist for song in songs))
        return sorted(artists)


songs_service = SongsService()
