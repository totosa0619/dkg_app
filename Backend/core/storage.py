from storages.backends.azure_storage import AzureStorage

from dkvadmin import settings


class AzureStaticStorage(AzureStorage):
    connection_string = settings.AZURE_CONNECTION_STRING
    file_overwrite = False
