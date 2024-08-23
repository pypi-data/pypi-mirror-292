import dataclasses
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from orjson import orjson
from PIL import Image

from picsellia.exceptions import UploadError
from picsellia.exif import read_image_metadata
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.datasource import DataSource
from picsellia.services.error_manager import ErrorManager
from picsellia.types.enums import DataType, ObjectDataType
from picsellia.utils import filter_payload

ALLOWED_IMAGE_CONTENT_TYPES = (
    "image/jpeg",
    "image/bmp",
    "image/gif",
    "image/png",
    "image/tiff",
)

logger = logging.getLogger("picsellia")


@dataclasses.dataclass
class ProcessedDatum:
    data_type: DataType
    meta: Optional[Dict] = None
    metadata: Optional[Dict] = None


class DataUploader:
    def __init__(
        self,
        connexion: Connexion,
        datalake_id: UUID,
        connector_id: Optional[UUID],
        computed_tag_ids: List[UUID],
        source: Optional[DataSource],
        fill_metadata: bool,
        error_manager: Optional[ErrorManager],
    ):
        self.connexion = connexion
        self.connector_id = connector_id
        self.datalake_id = datalake_id
        self.error_manager = error_manager
        self.fill_metadata = fill_metadata
        self.computed_tags_ids = computed_tag_ids
        self.source = source

    def upload(self, items: Tuple[Union[str, Path], Optional[Dict]]):
        path, metadatum = items
        try:
            filename = os.path.split(path)[-1]
            object_name = self.connexion.generate_data_object_name(
                filename, ObjectDataType.DATA, self.connector_id
            )
            _, _, content_type = self.connexion.upload_file(
                object_name, path, connector_id=self.connector_id
            )
            payload = self._prepare_payload(
                filename, object_name, path, content_type, metadatum
            )
            return self.connexion.post(
                f"/api/datalake/{self.datalake_id}/datas",
                data=orjson.dumps(payload),
            )
        except Exception as e:
            message = f"Could not upload path '{path}'"
            logger.error(message, exc_info=e)
            if self.error_manager:
                self.error_manager.append(
                    UploadError(message=message, path=path, parent=e)
                )
            return None

    def _prepare_payload(
        self,
        filename: str,
        object_name: str,
        path: str,
        content_type: str,
        metadatum: dict,
    ):
        meta = None
        metadata = filter_payload(metadatum) if metadatum else None

        if content_type in ALLOWED_IMAGE_CONTENT_TYPES:
            data_type = DataType.IMAGE
            exif_data = self.prepare_metadata_from_image(
                path, metadatum, self.fill_metadata
            )
            if exif_data:
                meta = {"width": exif_data.width, "height": exif_data.height}
                metadata = exif_data.metadata
        elif content_type.startswith("video/"):
            data_type = DataType.VIDEO
        else:
            data_type = DataType.IMAGE
            logger.info(
                f"SDK cannot open {path} because its content type {content_type} is not openable here. "
                f"We will still upload your data and try handle it in our backend services."
            )

        payload = {
            "type": data_type,
            "filename": filename,
            "object_name": object_name,
            "content_type": content_type,
            "tags": self.computed_tags_ids,
            "data_source_id": self.source.id if self.source else None,
        }
        if meta:
            payload["meta"] = meta
        if metadata:
            payload["metadata"] = metadata
        return payload

    @staticmethod
    def prepare_metadata_from_image(path: str, metadatum: dict, fill_metadata: bool):
        try:
            # Try opening with Pillow to read exif metadata, width and height
            with Image.open(path) as image:
                return read_image_metadata(image, metadatum, fill_metadata)
        except Exception:
            logger.error(
                f"{path} could not be opened with Pillow, Picsellia will try to compute size of this image later."
            )
            return None
