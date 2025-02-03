import logging
import os
from typing import Optional

from django.conf import settings
from django.core.files.storage import Storage
from storages.backends.azure_storage import AzureStorage

logger = logging.getLogger("azure")

def new_client() -> Storage:
    return AzureStorage(
        connection_string=settings.AZURE_CONNECTION_STRING,
        azure_container=settings.AZURE_CONTAINER,
    )


def upload_diagram(cl: Storage, local_path: str, blob_name: Optional[str] = None) -> str:
    if blob_name is None:
        blob_name = os.path.basename(local_path)

    with open(local_path, "rb") as blob:
        logger.info("uploading %s", blob_name)
        return cl.save(blob_name, blob)

def get_path(name: str, cl: Storage) -> str:
    if cl:
        return cl.path(name)

    return f"{settings.AZURE_BLOB_PATH}/{name}"
