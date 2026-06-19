# exif-time-shift

CLI tool to shift the EXIF date/time of all photos in a directory. Useful when a camera's clock was wrong
(e.g. wrong timezone or drifted time) and you want to correct timestamps in bulk.

Supports **JPEG** (`.jpg`/`.jpeg`) and **Sony RAW** (`.arw`) files.

## Installation

```bash
pip install exif-time-shift
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install exif-time-shift
```

## Usage

```text
exif-time-shift <directory> <minutes>
```

- `<directory>` — folder containing photos to update (non-recursively)
- `<minutes>` — integer offset in minutes (positive = forward, negative = backward)

## Examples

```bash
# Photos were taken 90 minutes ahead — subtract 90 minutes
exif-time-shift /photos/vacation -90

# Camera was set to UTC but should be UTC+2 — add 120 minutes
exif-time-shift ./raw_files 120
```

Output per file:

```text
/photos/vacation/IMG_001.jpg: 2024:07:15 14:30:00 -> 2024:07:15 13:00:00
/photos/vacation/IMG_002.arw: 2024:07:15 14:31:10 -> 2024:07:15 13:01:10
```

## What gets updated

The following EXIF fields are shifted in each file:

| Field               | Description                  |
| ------------------- | ---------------------------- |
| `DateTime`          | Main image date/time         |
| `DateTimeOriginal`  | When the shutter was pressed |
| `DateTimeDigitized` | When the image was digitized |
