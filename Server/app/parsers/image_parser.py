from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class ImageParser(BaseParser):
    """
    Forensic Image Metadata Parser.
    Extracts EXIF metadata, timestamps, camera make/model, and normalized decimal GPS coordinates.
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
                        gps_info[gps_tag_name] = gps_val
                else:
                    if isinstance(value, (str, int, float)):
                        parsed_exif[tag_name] = value
                    elif isinstance(value, bytes):
                        parsed_exif[tag_name] = value.decode("utf-8", errors="ignore")

            # Extract timestamp
            raw_ts = (
                parsed_exif.get("DateTimeOriginal")
                or parsed_exif.get("DateTime")
                or parsed_exif.get("DateTimeDigitized")
            )
            parsed_ts = self.parse_datetime(raw_ts)

            # Camera metadata
            camera_make = parsed_exif.get("Make", "UNKNOWN")
            camera_model = parsed_exif.get("Model", "UNKNOWN")
            software = parsed_exif.get("Software", "UNKNOWN")

            # Resolve decimal GPS coordinates
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
            if coords:
                content["latitude"] = coords["latitude"]
                content["longitude"] = coords["longitude"]
                content["map_location"] = coords["coordinates"]

            artifacts.append({
                "artifact_type": "IMAGE_METADATA",
                "timestamp": parsed_ts,
                "source": "IMAGE_EXIF",
                "content": content,
                "raw_data": str(parsed_exif),
                "metadata": {
                    "raw_exif": parsed_exif,
                    "file_size": path.stat().st_size if path.exists() else 0,
                    "has_gps": coords is not None,
                },
            })

        except ImportError:
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
            # If image has stripped EXIF or is corrupt, return basic metadata record
            artifacts.append({
                "artifact_type": "IMAGE_METADATA",
                "timestamp": None,
                "source": "IMAGE_RAW",
                "content": {
                    "filename": path.name,
                    "note": f"Image metadata note: {str(e)}",
                },
                "raw_data": str(e),
                "metadata": {},
            })

        return artifacts

    def _extract_coordinates(self, gps_info: dict) -> dict[str, Any] | None:
        try:
            lat_data = gps_info.get("GPSLatitude")
            lat_ref = gps_info.get("GPSLatitudeRef", "N")
            lon_data = gps_info.get("GPSLongitude")
            lon_ref = gps_info.get("GPSLongitudeRef", "E")

            if not lat_data or not lon_data:
                return None

            lat = self._convert_to_degrees(lat_data)
            if str(lat_ref).upper() in ["S", "SOUTH"]:
                lat = -lat

            lon = self._convert_to_degrees(lon_data)
            if str(lon_ref).upper() in ["W", "WEST"]:
                lon = -lon

            return {
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "coordinates": f"{round(lat, 6)}, {round(lon, 6)}",
            }
        except Exception:
            return None

    @staticmethod
    def _convert_to_degrees(value: Any) -> float:
        try:
            if isinstance(value, (tuple, list)) and len(value) >= 3:
                d = float(value[0])
                m = float(value[1])
                s = float(value[2])
                return d + (m / 60.0) + (s / 3600.0)
            return float(value)
        except Exception:
            return 0.0
