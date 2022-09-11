import os
from io import BytesIO

from tinytag import TinyTag
from PIL import Image, UnidentifiedImageError

from app import settings
from app.utils import create_hash


def parse_album_art(filepath: str):
    """
    Returns the album art for a given audio file.
    """

    try:
        tags = TinyTag.get(filepath, image=True)
        return tags.get_image()
    except:
        return None


def extract_thumb(filepath: str, webp_path: str) -> bool:
    """
    Extracts the thumbnail from an audio file. Returns the path to the thumbnail.
    """
    img_path = os.path.join(settings.THUMBS_PATH, webp_path)
    tsize = settings.THUMB_SIZE

    if os.path.exists(img_path):
        img_size = os.path.getsize(filepath)

        if img_size > 0:
            return True

    album_art = parse_album_art(filepath)

    if album_art is not None:
        try:
            img = Image.open(BytesIO(album_art))
        except (UnidentifiedImageError, OSError):
            return False

        try:
            small_img = img.resize((tsize, tsize), Image.ANTIALIAS)
            small_img.save(img_path, format="webp")
        except OSError:
            try:
                png = img.convert("RGB")
                small_img = png.resize((tsize, tsize), Image.ANTIALIAS)
                small_img.save(webp_path, format="webp")
            except:
                return False

        return True
    else:
        return False


def get_tags(filepath: str):
    filetype = filepath.split(".")[-1]
    filename = (filepath.split("/")[-1]).replace(f".{filetype}", "")

    try:
        tags = TinyTag.get(filepath)
    except:
        return None

    if tags.artist == "":
        tags.artist = tags.albumartist

    if (tags.title == "") or (tags.title is None):
        tags.title = filename

    to_check = ["album", "artist", "albumartist", "year"]
    for prop in to_check:
        p = getattr(tags, prop)
        if (p is None) or (p == ""):
            setattr(tags, prop, "Unknown")

    to_round = ["bitrate", "duration"]
    for prop in to_round:
        try:
            setattr(tags, prop, round(getattr(tags, prop)))
        except TypeError:
            setattr(tags, prop, 0)

    to_int = ["track", "disc"]
    for prop in to_int:
        try:
            setattr(tags, prop, int(getattr(tags, prop)))
        except (ValueError, TypeError):
            setattr(tags, prop, 1)

    try:
        tags.copyright = tags.extra["copyright"]
    except KeyError:
        tags.copyright = None

    tags.albumhash = create_hash(tags.album, tags.albumartist)
    tags.hash = create_hash(tags.artist, tags.album, tags.title)
    tags.image = f"{tags.albumhash}.webp"
    tags.folder = os.path.dirname(filepath)

    tags.date = tags.year
    tags.filepath = filepath
    tags.filetype = filetype

    tags = tags.__dict__

    # delete all tag properties that start with _ (tinytag internals)
    for tag in list(tags):
        if tag.startswith("_"):
            del tags[tag]

    to_delete = [
        "filesize",
        "audio_offset",
        "channels",
        "comment",
        "composer",
        "disc_total",
        "extra",
        "samplerate",
        "track_total",
        "year",
    ]

    for tag in to_delete:
        del tags[tag]

    return tags
