import sys
import os
from datetime import datetime, timedelta
from PIL import Image

EXIF_DATE_TAG = 306
EXIF_DATE_ORIGINAL = 36867
EXIF_DATE_DIGITIZED = 36868


def parse_exif_date(date_str):
    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")


def format_exif_date(dt):
    return dt.strftime("%Y:%m:%d %H:%M:%S")


def shift_jpeg(filepath, minutes):
    img = Image.open(filepath)
    exif = img.getexif()

    # Get Exif sub-IFD
    exif_ifd = exif.get_ifd(0x8769)

    # Find original date - check sub-IFD first, then main EXIF
    if exif_ifd and EXIF_DATE_ORIGINAL in exif_ifd:
        original_date_str = exif_ifd[EXIF_DATE_ORIGINAL]
    elif EXIF_DATE_TAG in exif:
        original_date_str = exif[EXIF_DATE_TAG]
    else:
        print(f"No DateTime or DateTimeOriginal tag found in {filepath}")
        return

    original_date = parse_exif_date(original_date_str)
    new_date = original_date + timedelta(minutes=minutes)
    new_date_str = format_exif_date(new_date)

    # Update main EXIF
    exif[EXIF_DATE_TAG] = new_date_str
    if EXIF_DATE_ORIGINAL in exif:
        exif[EXIF_DATE_ORIGINAL] = new_date_str
    if EXIF_DATE_DIGITIZED in exif:
        exif[EXIF_DATE_DIGITIZED] = new_date_str

    # Update Exif sub-IFD
    if exif_ifd:
        if EXIF_DATE_ORIGINAL in exif_ifd:
            exif_ifd[EXIF_DATE_ORIGINAL] = new_date_str
        if EXIF_DATE_DIGITIZED in exif_ifd:
            exif_ifd[EXIF_DATE_DIGITIZED] = new_date_str

    img.save(filepath, exif=exif)
    print(f"{filepath}: {original_date_str} -> {new_date_str}")


def shift_arw(filepath, minutes):
    import pyexiv2

    img = pyexiv2.Image(filepath)
    exif = img.read_exif()

    # Find original date
    if "Exif.Photo.DateTimeOriginal" in exif:
        original_date_str = exif["Exif.Photo.DateTimeOriginal"]
    elif "Exif.Image.DateTime" in exif:
        original_date_str = exif["Exif.Image.DateTime"]
    else:
        print(f"No DateTime or DateTimeOriginal tag found in {filepath}")
        return

    original_date = parse_exif_date(original_date_str)
    new_date = original_date + timedelta(minutes=minutes)
    new_date_str = format_exif_date(new_date)

    # Update dates using pyexiv2
    img.modify_exif(
        {
            "Exif.Image.DateTime": new_date_str,
            "Exif.Photo.DateTimeOriginal": new_date_str,
            "Exif.Photo.DateTimeDigitized": new_date_str,
            "Exif.Thumbnail.DateTime": new_date_str,
        }
    )

    print(f"{filepath}: {original_date_str} -> {new_date_str}")


def shift_exif_date(filepath, minutes):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".jpg", ".jpeg"):
        shift_jpeg(filepath, minutes)
    elif ext == ".arw":
        shift_arw(filepath, minutes)
    else:
        print(f"Unsupported file format: {filepath}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <directory> <minutes>")
        sys.exit(1)

    directory = sys.argv[1]

    try:
        minutes = int(sys.argv[2])
    except ValueError:
        print(f"Error: '{sys.argv[2]}' is not a valid integer")
        sys.exit(1)

    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a directory")
        sys.exit(1)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and filename.lower().endswith(
            (".jpg", ".jpeg", ".arw")
        ):
            try:
                shift_exif_date(filepath, minutes)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")


if __name__ == "__main__":
    main()
