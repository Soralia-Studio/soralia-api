from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from sqlmodel import Field, SQLModel


class SheetType(str, Enum):
    DX = "dx"
    STD = "std"
    UTAGE = "utage"


class Difficulty(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    RE_MASTER = "remaster"


class NoteCounts(SQLModel):
    tap: Optional[int] = Field(default=None)
    hold: Optional[int] = Field(default=None)
    slide: Optional[int] = Field(default=None)
    touch: Optional[int] = Field(default=None)
    break_: Optional[int] = Field(alias="break", default=None)
    total: Optional[int] = Field(default=None)


class Regions(SQLModel):
    jp: bool = Field(default=False)
    intl: bool = Field(default=False)
    cn: bool = Field(default=False)


class RegionOverrides(SQLModel):
    intl: Dict[str, Any] = Field(default_factory=dict)


class Sheet(SQLModel):
    type: SheetType = Field(default=SheetType.DX)
    difficulty: Difficulty = Field(default=Difficulty.BASIC)
    level: str = Field(default="1")
    level_value: float = Field(alias="levelValue", default=1.0)
    internal_level: Optional[str] = Field(default=None, alias="internalLevel")
    internal_level_value: float = Field(alias="internalLevelValue", default=1.0)
    note_designer: str = Field(alias="noteDesigner", default="-")
    note_counts: NoteCounts = Field(alias="noteCounts", default_factory=NoteCounts)
    regions: Regions = Field(default_factory=Regions)
    region_overrides: RegionOverrides = Field(
        alias="regionOverrides", default_factory=RegionOverrides
    )
    is_special: bool = Field(alias="isSpecial", default=False)
    version: str = Field(default="")


class Song(SQLModel):
    song_id: str = Field(alias="songId", default="")
    category: str = Field(default="")
    title: str = Field(default="")
    artist: str = Field(default="")
    bpm: int = Field(default=0)
    image_name: str = Field(alias="imageName", default="")
    version: str = Field(default="")
    release_date: date = Field(alias="releaseDate", default_factory=date.today)
    is_new: bool = Field(alias="isNew", default=False)
    is_locked: bool = Field(alias="isLocked", default=False)
    comment: Optional[str] = Field(default=None)
    sheets: list[Sheet] = Field(default_factory=list)


class SongResponse(Song):
    pass


class SongsListResponse(SQLModel):
    songs: list[Song] = Field(default_factory=list)
    total: int = Field(default=0)


class SongSearchParams(SQLModel):
    title: Optional[str] = Field(default=None)
    artist: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)
    difficulty: Optional[Difficulty] = Field(default=None)
    level_min: Optional[float] = Field(default=None)
    level_max: Optional[float] = Field(default=None)
    bpm_min: Optional[int] = Field(default=None)
    bpm_max: Optional[int] = Field(default=None)
    is_new: Optional[bool] = Field(default=None)
    is_locked: Optional[bool] = Field(default=None)
    sheet_type: Optional[SheetType] = Field(default=None)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, le=1000, ge=1)
