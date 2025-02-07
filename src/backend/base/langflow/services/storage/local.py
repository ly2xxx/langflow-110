import asyncio
from pathlib import Path

from loguru import logger

from .service import StorageService


class LocalStorageService(StorageService):
    """A service class for handling local storage operations without aiofiles."""

    def __init__(self, session_service, settings_service) -> None:
        """Initialize the local storage service with session and settings services."""
        super().__init__(session_service, settings_service)
        self.data_dir = Path(settings_service.settings.config_dir)
        self.set_ready()

    def build_full_path(self, flow_id: str, file_name: str) -> str:
        """Build the full path of a file in the local storage."""
        return str(self.data_dir / flow_id / file_name)

    async def save_file(self, flow_id: str, file_name: str, data: bytes) -> None:
        """Save a file in the local storage.

        :param flow_id: The identifier for the flow.
        :param file_name: The name of the file to be saved.
        :param data: The byte content of the file.
        :raises FileNotFoundError: If the specified flow does not exist.
        :raises IsADirectoryError: If the file name is a directory.
        :raises PermissionError: If there is no permission to write the file.
        """
        folder_path = self.data_dir / flow_id
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / file_name

        def write_file(file_path: Path, data: bytes) -> None:
            file_path.write_bytes(data)

        try:
            await asyncio.to_thread(write_file, file_path, data)
            logger.info(f"File {file_name} saved successfully in flow {flow_id}.")
        except Exception:
            logger.exception(f"Error saving file {file_name} in flow {flow_id}")
            raise

    async def get_file(self, flow_id: str, file_name: str) -> bytes:
        """Retrieve a file from the local storage.

        :param flow_id: The identifier for the flow.
        :param file_name: The name of the file to be retrieved.
        :return: The byte content of the file.
        :raises FileNotFoundError: If the file does not exist.
        """
        file_path = self.data_dir / flow_id / file_name
        if not file_path.exists():
            logger.warning(f"File {file_name} not found in flow {flow_id}.")
            msg = f"File {file_name} not found in flow {flow_id}"
            raise FileNotFoundError(msg)

        def read_file(file_path: Path) -> bytes:
            return file_path.read_bytes()

        content = await asyncio.to_thread(read_file, file_path)
        logger.debug(f"File {file_name} retrieved successfully from flow {flow_id}.")
        return content

    async def list_files(self, flow_id: str):
        """List all files in a specified flow.

        :param flow_id: The identifier for the flow.
        :return: A list of file names.
        :raises FileNotFoundError: If the flow directory does not exist.
        """
        folder_path = self.data_dir / flow_id
        if not folder_path.exists() or not folder_path.is_dir():
            logger.warning(f"Flow {flow_id} directory does not exist.")
            msg = f"Flow {flow_id} directory does not exist."
            raise FileNotFoundError(msg)

        files = [file.name for file in folder_path.iterdir() if file.is_file()]
        logger.info(f"Listed {len(files)} files in flow {flow_id}.")
        return files

    async def delete_file(self, flow_id: str, file_name: str) -> None:
        """Delete a file from the local storage.

        :param flow_id: The identifier for the flow.
        :param file_name: The name of the file to be deleted.
        """
        file_path = self.data_dir / flow_id / file_name
        if file_path.exists():
            file_path.unlink()
            logger.info(f"File {file_name} deleted successfully from flow {flow_id}.")
        else:
            logger.warning(f"Attempted to delete non-existent file {file_name} in flow {flow_id}.")

    async def teardown(self) -> None:
        """Perform any cleanup operations when the service is being torn down."""
        # No specific teardown actions required for local
