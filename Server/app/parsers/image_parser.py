from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class ImageParser(BaseParser):
    """
    Forensic Image Metadata Parser.
    Extracts EXIF metadata, timestamps, camera make/model, and GPS coordinates from image evidence.
    """

    def parse(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []
        path = Path(file_path)

        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS

            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format or path.suffix.replace(".", "").upper()
                exif_data = img._getexif() or {}

            parsed_exif = {}
            gps_info = {}

            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)

                if tag_name == "GPSInfo":
                    for gps_tag_id, gps_val in value.items():
                        gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag_name] = str(gps_val)
                else:
                    # Filter string or numeric values
                    if isinstance(value, (str, int, float)):
                        parsed_exif[tag_name] = value
                    elif isinstance(value, bytes):
                        parsed_exif[tag_name] = value.decode("utf-8", errors="ignore")

            # Extract timestamp
            raw_ts = parsed_exif.get("DateTimeOriginal") or parsed_exif.get("DateTime") or parsed_exif.get("DateTimeDigitized")
            parsed_ts = self.parse_datetime(raw_ts)

            # Camera metadata
            camera_make = parsed_exif.get("Make", "UNKNOWN")
            camera_model = parsed_exif.get("Model", "UNKNOWN")
            software = parsed_exif.get("Software", "UNKNOWN")

            # Resolve GPS if available
            coords = self._extract_coordinates(gps_info)

            content = {
                "filename": path.name,
                "format": format_name,
                "width": width,
                "height": height,
                "camera_make": camera_make,
                "camera_model": camera_model,
                "software": software,
                "gps_coordinates": coords,
                "exif_summary": f"{camera_make} {camera_model} | {width}x{height} | {format_name}",
            }

            artifacts.append({
                "artifact_type": "IMAGE_METADATA",
                "timestamp": parsed_ts,
                "source": "IMAGE_EXIF",
                "content": content,
                "raw_data": str(parsed_exif),
                "metadata": {
                    "raw_exif": parsed_exif,
                    "gps_raw": gps_info,
                    "file_size": path.stat().st_size,
                },
            })

        except ImportError:
            # Fallback if Pillow is not available
            artifacts.append({
                "artifact_type": "IMAGE_METADATA",
                "timestamp": None,
                "source": "IMAGE_RAW",
                "content": {
                    "filename": path.name,
                    "file_size": path.stat().st_size if path.exists() else 0,
                    "note": "Pillow not available for EXIF extraction",
                },
                "raw_data": path.name,
                "metadata": {},
            })
        except Exception as e:
            # If image has no EXIF or is corrupt, return basic metadata record
            artifacts.append({
                "artifact_type": "IMAGE_METADATA",
                "timestamp": None,
                "source": "IMAGE_RAW",
                "content": {
                    "filename": path.name,
                    "note": f"Image metadata extraction note: {str(e)}",
                },
                "raw_data": str(e),
                "metadata": {},
            })

        return artifacts

    def _extract_coordinates(self, gps_info: dict) -> dict[str, float] | None:
        try:
            lat_data = gps_info.get("GPSLatitude")
            lat_ref = gps_info.get("GPSLatitudeRef", "N")
            lon_data = gps_info.get("GPSLongitude")
            lon_ref = gps_info.get("GPSLongitudeRef", "E")

            if not lat_data or not lon_data:
                return None

            # Simple coordinate parsing if tuple/list representation
            return {
                "latitude_raw": str(lat_data),
                "latitude_ref": str(lat_ref),
                "longitude_raw": str(lon_data),
                "longitude_ref": str(lon_ref),
            }
        except Exception:
            return None
