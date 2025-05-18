import asyncio
import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from google.api_core.exceptions import NotFound
from google.cloud import storage


class GoogleStorageConnector:
    def __init__(
        self, project_id: Optional[str] = None, logger: Optional[logging.Logger] = None
    ):
        self.client = storage.Client(project=project_id)
        self.logger = logger or logging.getLogger(__name__)

    # Synchronous methods
    def download_blob(self, bucket_name: str, blob_name: str) -> bytes:
        """
        Download a blob from Google Cloud Storage synchronously.

        :param bucket_name: Name of the bucket
        :param blob_name: Name of the blob (file) to download
        :return: Content of the blob as bytes
        """
        self.logger.info(f"Downloading {blob_name} from {bucket_name}")

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            content = blob.download_as_bytes()
            self.logger.info(f"Successfully downloaded {blob_name} from {bucket_name}")
            return content
        except NotFound:
            self.logger.error(f"Blob {blob_name} not found in bucket {bucket_name}")
            raise FileNotFoundError(
                f"Blob {blob_name} not found in bucket {bucket_name}"
            )
        except Exception as e:
            self.logger.error(
                f"Error downloading {blob_name} from {bucket_name}: {str(e)}"
            )
            raise

    def upload_blob(
        self,
        bucket_name: str,
        blob_name: str,
        file_path: Union[str, Path],
        is_public: bool = False,
    ) -> None:
        """
        Upload a blob to Google Cloud Storage synchronously.

        :param bucket_name: Name of the bucket
        :param blob_name: Name of the blob (file) to upload
        :param file_path: Path to the local file to upload
        :param is_public: Whether to make the blob public after upload
        """
        self.logger.info(f"Uploading {blob_name} to {bucket_name}")

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            self.logger.info(f"Successfully uploaded {blob_name} to {bucket_name}")
            blob.upload_from_filename(file_path)
            if is_public:
                blob.make_public()
                self.logger.info(f"Blob {blob_name} is now public")
            return blob.public_url

        except Exception as e:
            self.logger.error(f"Error uploading {blob_name} to {bucket_name}: {str(e)}")
            raise

    def list_blobs(self, bucket_name: str, prefix: Optional[str] = None) -> List[str]:
        """
        List blobs in a bucket synchronously.

        :param bucket_name: Name of the bucket
        :param prefix: Optional prefix to filter blobs
        :return: List of blob names
        """
        self.logger.info(
            f"Listing blobs in {bucket_name}"
            + (f" with prefix {prefix}" if prefix else "")
        )

        try:
            blobs = [
                blob.name for blob in self.client.list_blobs(bucket_name, prefix=prefix)
            ]
            self.logger.info(f"Successfully listed blobs in {bucket_name}")
            return blobs
        except Exception as e:
            self.logger.error(f"Error listing blobs in {bucket_name}: {str(e)}")
            raise

    def download_folder(
        self, bucket_name: str, gcs_folder: str, local_folder: str
    ) -> None:
        """
        Download all blobs from a Google Cloud Storage folder to a local folder synchronously.

        :param bucket_name: Name of the bucket
        :param gcs_folder: Path to the GCS folder to download
        :param local_folder: Path to the local folder to save files
        """
        self.logger.info(
            f"Downloading folder {gcs_folder} from {bucket_name} to {local_folder}"
        )

        try:
            # List all blobs in the GCS folder
            blobs = self.list_blobs(bucket_name, prefix=gcs_folder)

            for blob_name in blobs:
                # Ignore if the blob is a "folder" (ends with '/')
                if blob_name.endswith("/"):
                    continue

                # Construct the local file path
                relative_path = os.path.relpath(blob_name, gcs_folder)
                local_file_path = os.path.join(local_folder, relative_path)

                # Ensure local subdirectories exist
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Download the blob content
                content = self.download_blob(bucket_name, blob_name)

                # Write the content to the local file
                with open(local_file_path, "wb") as f:
                    f.write(content)

                self.logger.info(f"Downloaded: {blob_name} -> {local_file_path}")

        except Exception as e:
            self.logger.error(
                f"Error downloading folder {gcs_folder} from bucket {bucket_name}: {str(e)}"
            )
            raise

    # Asynchronous methods
    async def download_blob_async(self, bucket_name: str, blob_name: str) -> bytes:
        """
        Download a blob from Google Cloud Storage asynchronously.

        :param bucket_name: Name of the bucket
        :param blob_name: Name of the blob (file) to download
        :return: Content of the blob as bytes
        """
        self.logger.info(f"Initiating async download of {blob_name} from {bucket_name}")
        return await asyncio.to_thread(self.download_blob, bucket_name, blob_name)

    async def upload_blob_async(
        self,
        bucket_name: str,
        blob_name: str,
        file_path: Union[str, Path],
        is_public: bool = False,
    ) -> None:
        """
        Upload a blob to Google Cloud Storage asynchronously.

        :param bucket_name: Name of the bucket
        :param blob_name: Name of the blob (file) to upload
        :param file_path: Path to the local file to upload
        :param is_public: Whether to make the blob public after upload
        """
        self.logger.info(f"Initiating async upload of {blob_name} to {bucket_name}")
        await asyncio.to_thread(
            self.upload_blob, bucket_name, blob_name, file_path, is_public
        )

    async def list_blobs_async(
        self, bucket_name: str, prefix: Optional[str] = None
    ) -> List[str]:
        """
        List blobs in a bucket asynchronously.

        :param bucket_name: Name of the bucket
        :param prefix: Optional prefix to filter blobs
        :return: List of blob names
        """
        self.logger.info(
            f"Listing blobs in {bucket_name} asynchronously"
            + (f" with prefix {prefix}" if prefix else "")
        )
        return await asyncio.to_thread(self.list_blobs, bucket_name, prefix)

    async def download_folder_async(
        self, bucket_name: str, gcs_folder: str, local_folder: str
    ) -> None:
        """
        Download all blobs from a Google Cloud Storage folder to a local folder asynchronously.

        :param bucket_name: Name of the bucket
        :param gcs_folder: Path to the GCS folder to download
        :param local_folder: Path to the local folder to save files
        """
        self.logger.info(
            f"Initiating async download of folder {gcs_folder} from {bucket_name} to {local_folder}"
        )

        try:
            # List all blobs in the GCS folder
            blobs = await self.list_blobs_async(bucket_name, prefix=gcs_folder)

            # Create a list of download tasks
            download_tasks = []
            for blob_name in blobs:
                # Ignore if the blob is a "folder" (ends with '/')
                if blob_name.endswith("/"):
                    continue

                # Construct the local file path
                relative_path = os.path.relpath(blob_name, gcs_folder)
                local_file_path = os.path.join(local_folder, relative_path)

                # Ensure local subdirectories exist
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Create download task
                task = self._download_and_save(bucket_name, blob_name, local_file_path)
                download_tasks.append(task)

            # Execute all downloads concurrently
            await asyncio.gather(*download_tasks)
            self.logger.info(f"Completed async download of folder {gcs_folder}")

        except Exception as e:
            self.logger.error(
                f"Error downloading folder {gcs_folder} from bucket {bucket_name}: {str(e)}"
            )
            raise

    async def _download_and_save(
        self, bucket_name: str, blob_name: str, local_file_path: str
    ) -> None:
        """Helper method to download a blob and save it to a local path."""
        content = await self.download_blob_async(bucket_name, blob_name)

        # Write the content to the local file
        with open(local_file_path, "wb") as f:
            f.write(content)

        self.logger.info(f"Downloaded: {blob_name} -> {local_file_path}")


# Create a singleton instance that can be imported elsewhere
storage_connector = GoogleStorageConnector()
