from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class ImageParser(BaseParser):
    """
    Forensic Image Metadata Parser.
    Extracts EXIF metadata, timestamps, camera make/model, and normalized decimal GPS coordinates.
    Distinguishes source metadata absence from parsing errors to prevent false 'UNKNOWN UNKNOWN' output.
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

            # Camera metadata distinction: absent in source vs populated
            has_exif = bool(exif_data)
            camera_make = parsed_exif.get("Make")
            camera_model = parsed_exif.get("Model")
            software = parsed_exif.get("Software")

            if camera_make or camera_model:
                camera_str = f"{camera_make or ''} {camera_model or ''}".strip()
                exif_summary = f"{camera_str} | {width}x{height} | {format_name}"
                metadata_status = "EXIF_PRESENT_WITH_DEVICE_DATA"
            elif has_exif:
                camera_str = "No Device Identifier"
                exif_summary = f"No Device Identifier | {width}x{height} | {format_name}"
                metadata_status = "EXIF_PRESENT_WITHOUT_DEVICE_DATA"
            else:
                camera_str = "No EXIF Embedded"
                exif_summary = f"No EXIF Embedded (Metadata absent in source file) | {width}x{height} | {format_name}"
                metadata_status = "METADATA_ABSENT_IN_SOURCE"

            # Resolve decimal GPS coordinates
            coords = self._extract_coordinates(gps_info)

            content = {
                "filename": path.name,
                "format": format_name,
                "width": width,
                "height": height,
                "camera_make": camera_make,
                "camera_model": camera_model,
                "camera_display": camera_str,
                "software": software,
                "gps_coordinates": coords,
                "metadata_status": metadata_status,
                "exif_summary": exif_summary,
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
                "raw_data": str(parsed_exif) if parsed_exif else "No raw EXIF bytes present",
                "metadata": {
                    "raw_exif": parsed_exif,
                    "metadata_status": metadata_status,
                    "file_size": path.stat().st_size if path.exists() else 0,
                    "has_gps": coords is not None,
                    "has_exif_timestamp": parsed_ts is not None,
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
                    "metadata_status": "PARSER_DEPENDENCY_MISSING",
                    "note": "Pillow not available for EXIF extraction",
                },
                "raw_data": path.name,
                "metadata": {"metadata_status": "PARSER_DEPENDENCY_MISSING"},
            })
        except Exception as e:
            artifacts.append({
                "artifact_type": "IMAGE_METADATA",
                "timestamp": None,
                "source": "IMAGE_RAW",
                "content": {
                    "filename": path.name,
                    "metadata_status": "PARSER_EXCEPTION",
                    "note": f"Metadata extraction failed: {str(e)}",
                },
                "raw_data": str(e),
                "metadata": {"metadata_status": "PARSER_EXCEPTION"},
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
