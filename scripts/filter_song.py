import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from pydantic import ValidationError

from src.models import Song

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("filter_song.log", mode="w", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def convert_date_field(song_data: Dict[str, Any]) -> Dict[str, Any]:
    if song_data.get("releaseDate"):
        try:
            song_data["releaseDate"] = datetime.strptime(
                song_data["releaseDate"], "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Invalid date format for song '{song_data.get('title', 'Unknown')}': {e}"
            )

    return song_data


def validate_song(song_data: Dict[str, Any]) -> Tuple[bool, Song | None, str]:
    try:
        processed_data = convert_date_field(song_data.copy())
        song = Song.model_validate(processed_data)
        return True, song, ""

    except ValidationError as e:
        error_msg = (
            f"Validation error for song '{song_data.get('title', 'Unknown')}': {e}"
        )
        return False, None, error_msg

    except Exception as e:
        error_msg = (
            f"Unexpected error for song '{song_data.get('title', 'Unknown')}': {e}"
        )
        return False, None, error_msg


def filter_songs(input_file: Path, output_file: Path) -> Dict[str, Any]:
    logger.info(f"Loading song data from: {input_file}")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading input file: {e}")
        sys.exit(1)

    original_songs = data.get("songs", [])
    logger.info(f"Total songs in input: {len(original_songs)}")

    valid_songs = []
    invalid_count = 0
    error_log = []

    for i, song_data in enumerate(original_songs):
        if i % 250 == 0:
            logger.info(f"Processing song {i + 1}/{len(original_songs)}")

        is_valid, validated_song, error_msg = validate_song(song_data)

        if is_valid:
            valid_songs.append(song_data)
        else:
            invalid_count += 1
            error_log.append(
                {
                    "index": i,
                    "song_id": song_data.get("songId", "Unknown"),
                    "title": song_data.get("title", "Unknown"),
                    "error": error_msg,
                }
            )

            if invalid_count <= 5:
                logger.warning(f"Invalid song found: {error_msg}")

    output_data = {
        "url_source": data.get("url_source", ""),
        "date": data.get("date", ""),
        "filtering_info": {
            "filtered_at": datetime.now().isoformat(),
            "original_count": len(original_songs),
            "valid_count": len(valid_songs),
            "invalid_count": invalid_count,
            "success_rate": f"{(len(valid_songs) / len(original_songs) * 100):.2f}%"
            if original_songs
            else "0%",
        },
        "songs": valid_songs,
    }

    logger.info(f"Saving filtered data to: {output_file}")
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving output file: {e}")
        sys.exit(1)

    error_file = None
    if error_log:
        error_file = output_file.parent / f"{output_file.stem}_errors.json"
        logger.info(f"Saving error log to: {error_file}")
        try:
            with open(error_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "filtering_info": output_data["filtering_info"],
                        "errors": error_log,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            logger.warning(f"Could not save error log: {e}")
            error_file = None

    return {
        "original_count": len(original_songs),
        "valid_count": len(valid_songs),
        "invalid_count": invalid_count,
        "success_rate": (len(valid_songs) / len(original_songs) * 100)
        if original_songs
        else 0,
        "error_log_file": error_file,
    }


def main():
    project_root = Path(__file__).parent.parent
    input_file = project_root / "data" / "maimai_song.json"
    output_file = project_root / "data" / "maimai_song_filtered.json"

    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)

    logger.info("Maimai Song Data Filter")
    logger.info("=" * 50)
    logger.info(f"Input:  {input_file}")
    logger.info(f"Output: {output_file}")

    start_time = datetime.now()
    stats = filter_songs(input_file, output_file)
    end_time = datetime.now()

    logger.info("=" * 50)
    logger.info("Filtering Complete!")
    logger.info(f"Processing time: {end_time - start_time}")
    logger.info("Results:")
    logger.info(f"   Original songs: {stats['original_count']:,}")
    logger.info(f"   Valid songs:    {stats['valid_count']:,}")
    logger.info(f"   Invalid songs:  {stats['invalid_count']:,}")
    logger.info(f"   Success rate:   {stats['success_rate']:.2f}%")

    if stats["error_log_file"]:
        logger.warning(f"Error log saved to: {stats['error_log_file']}")

    logger.info(f"Filtered data saved to: {output_file}")


if __name__ == "__main__":
    main()
