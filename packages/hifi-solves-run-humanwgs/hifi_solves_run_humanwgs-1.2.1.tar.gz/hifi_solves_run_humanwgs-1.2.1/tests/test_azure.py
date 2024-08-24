import unittest
from unittest.mock import patch
from io import StringIO
import os
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError,
    ServiceRequestError,
)
from hifi_solves_run_humanwgs.backends.azure import (
    validate_bucket,
    check_file_exists,
    upload_files,
)

# Azure Storage account information
storage_account = "bioscoastorage"
container_name = "hifi-solves-humanwgs-test-bucket"
blob_container = f"{storage_account}/{container_name}"

try:
    account_key = os.getenv("AZURE_ACCOUNT_KEY")
    if account_key is None:
        raise ValueError("AZURE_ACCOUNT_KEY environment variable is not set.")
except ValueError as e:
    raise SystemExit(f"✗ {e}")

try:
    credential = AzureNamedKeyCredential(storage_account, account_key)
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account}.blob.core.windows.net",
        credential=credential,
    )
except (ClientAuthenticationError, ServiceRequestError) as e:
    raise SystemExit(f"✗ Azure configuration error: {e}")
except Exception as e:
    raise SystemExit(f"✗ Unexpected error: {e}")


class TestValidateContainer(unittest.TestCase):
    def test_container_exists(self):
        formatted_container, path_prefix = validate_bucket(blob_container)
        self.assertEqual(formatted_container, blob_container)
        self.assertEqual(path_prefix, None)

    def test_container_does_not_exist(self):
        container = "hifi-solves-test-container"
        with self.assertRaisesRegex(SystemExit, "does not exist") as context:
            _, _ = validate_bucket(f"{storage_account}/{container}")

    def test_container_exists_with_path(self):
        formatted_container, path_prefix = validate_bucket(
            f"{blob_container}/hifi-uploads/my_path"
        )
        self.assertEqual(formatted_container, blob_container)
        self.assertEqual(path_prefix, "hifi-uploads/my_path")


class TestCheckFileExists(unittest.TestCase):
    bam_file = "HG002.bam"
    sample_id = "HG002"
    file_type = "bam"
    file_size_bytes = 12

    def setUp(self):
        with open(self.bam_file, "a") as f:
            # 12 bytes
            f.write("hello world\n")

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="my-custom-path/HG002.bam",
        )
        with open(self.bam_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="hifi-uploads/HG002/bam/HG002.bam",
        )
        with open(self.bam_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="HG002/bam/HG002.bam",
        )
        with open(self.bam_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

    def tearDown(self):
        os.remove(self.bam_file)
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="my-custom-path/HG002.bam",
        )
        blob_client.delete_blob()

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="hifi-uploads/HG002/bam/HG002.bam",
        )
        blob_client.delete_blob()

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="HG002/bam/HG002.bam",
        )
        blob_client.delete_blob()

    def test_blob_path_files_exist(self):
        path_prefix = None
        remote_file = f"/{blob_container}/my-custom-path/HG002.bam"
        file_exists, remote_path, file_size_bytes = check_file_exists(
            blob_container,
            path_prefix,
            remote_file,
            self.sample_id,
            self.file_type,
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "my-custom-path/HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)

    def test_blob_path_files_dont_exist(self):
        path_prefix = "hifi-uploads"
        remote_file = f"/{blob_container}/hifi-uploads/nonexistent/HG002.bam"
        file_exists, remote_path, file_size_bytes = check_file_exists(
            blob_container, path_prefix, remote_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "hifi-uploads/nonexistent/HG002.bam")
        self.assertEqual(file_size_bytes, None)

    def test_blob_path_wrong_container(self):
        path_prefix = "hifi-uploads"
        remote_file = f"/{storage_account}/wrong_container/hifi-uploads/HG002.bam"
        with self.assertRaisesRegex(SystemExit, "is outside of the target container."):
            _, _, _ = check_file_exists(
                blob_container, path_prefix, remote_file, self.sample_id, self.file_type
            )

    def test_local_path_files_exist_with_path_prefix(self):
        path_prefix = "hifi-uploads"
        file_exists, remote_path, file_size_bytes = check_file_exists(
            blob_container, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(
            remote_path,
            "hifi-uploads/HG002/bam/HG002.bam",
        )
        self.assertEqual(file_size_bytes, self.file_size_bytes)

    def test_local_path_files_exist_no_path_prefix(self):
        path_prefix = None
        file_exists, remote_path, file_size_bytes = check_file_exists(
            blob_container, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "HG002/bam/HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)

    def test_local_path_files_dont_exist(self):
        path_prefix = "nonexistent"
        file_exists, remote_path, file_size_bytes = check_file_exists(
            blob_container, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "nonexistent/HG002/bam/HG002.bam")
        self.assertEqual(file_size_bytes, None)


class TestUploadFiles(unittest.TestCase):
    bam_file = "HG002.bam"
    remote_path = "test/hifi-uploads/HG002.bam"

    def setUp(self):
        with open(self.bam_file, "a"):
            pass

    def tearDown(self):
        try:
            os.remove(self.bam_file)
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=self.remote_path
            )
            blob_client.delete_blob()
        except ResourceNotFoundError:
            # If the blob or container doesn't exist, ignore the error
            pass

    @patch("sys.stdout", new_callable=StringIO)
    def test_upload_succeeded(self, mock_stdout):
        files_to_upload = {self.bam_file: self.remote_path}
        upload_files(blob_container, files_to_upload)
        stdout = mock_stdout.getvalue().strip()
        self.assertEqual(
            stdout,
            f"Uploading files to target container\n\t✓ {os.path.basename(self.bam_file)}",
        )

    def test_upload_failed(self):
        nonexistent_container = "nonexistent-container"
        files_to_upload = {self.bam_file: self.remote_path}
        with self.assertRaisesRegex(
            SystemExit,
            f"Error uploading file {self.bam_file}: The specified container {nonexistent_container} does not exist.",
        ):
            upload_files(f"{storage_account}/{nonexistent_container}", files_to_upload)


if __name__ == "__main__":
    unittest.main()
