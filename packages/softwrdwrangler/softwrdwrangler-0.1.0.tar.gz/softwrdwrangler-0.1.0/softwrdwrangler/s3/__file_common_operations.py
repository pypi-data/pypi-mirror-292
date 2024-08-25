from datetime import datetime
from typing import Optional

import boto3

from .__utils import _parse_s3_uri


def list_files(s3_uri: str) -> list:
    """
    Lists files in a specified S3 bucket and prefix.

    :param s3_uri: S3 URI of the bucket and prefix, e.g. 's3://bucket-name/prefix/'
    :return: List of file keys.
    """
    s3_client = boto3.client("s3")
    bucket_name, prefix = _parse_s3_uri(s3_uri)

    if not bucket_name or not prefix:
        print("Invalid S3 URI.")
        return []

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = [content["Key"] for content in response.get("Contents", [])]
        return files
    except Exception as e:
        print(f"Error listing files in S3: {e}")
        return []


def delete_file(s3_uri: str) -> None:
    """
    Deletes a file from S3.

    :param s3_uri: S3 URI of the file to delete, e.g. 's3://bucket-name/path/to/file'
    """
    s3_client = boto3.client("s3")
    bucket_name, key = _parse_s3_uri(s3_uri)

    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        print(f"File {s3_uri} successfully deleted.")
    except Exception as e:
        print(f"Error deleting file from S3: {e}")


def upload_file(local_file_path: str, s3_uri: str) -> None:
    """
    Uploads a local file to S3.

    :param local_file_path: Path to the local file.
    :param s3_uri: S3 URI of the target location, e.g. 's3://bucket-name/path/to/file'
    """
    s3_client = boto3.client("s3")
    bucket_name, key = _parse_s3_uri(s3_uri)

    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return

    try:
        s3_client.upload_file(local_file_path, bucket_name, key)
        print(f"File {local_file_path} successfully uploaded to {s3_uri}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")


def download_file(s3_uri: str, local_file_path: str) -> None:
    """
    Downloads a file from S3 to a local path.

    :param s3_uri: S3 URI of the file to download, e.g. 's3://bucket-name/path/to/file'
    :param local_file_path: Path to the local file.
    """
    s3_client = boto3.client("s3")
    bucket_name, key = _parse_s3_uri(s3_uri)

    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return

    try:
        s3_client.download_file(bucket_name, key, local_file_path)
        print(f"File {s3_uri} successfully downloaded to {local_file_path}")
    except Exception as e:
        print(f"Error downloading file from S3: {e}")


def copy_file(src_s3_uri: str, dest_s3_uri: str) -> None:
    """
    Copies a file from one S3 location to another.

    :param src_s3_uri: Source S3 URI of the file to copy, e.g. 's3://src-bucket-name/path/to/file'
    :param dest_s3_uri: Destination S3 URI of the target location, e.g. 's3://dest-bucket-name/path/to/file'
    """
    s3_client = boto3.client("s3")
    src_bucket_name, src_key = _parse_s3_uri(src_s3_uri)
    dest_bucket_name, dest_key = _parse_s3_uri(dest_s3_uri)

    if not src_bucket_name or not src_key or not dest_bucket_name or not dest_key:
        print("Invalid S3 URI.")
        return

    try:
        copy_source = {"Bucket": src_bucket_name, "Key": src_key}
        s3_client.copy(copy_source, dest_bucket_name, dest_key)
        print(f"File {src_s3_uri} successfully copied to {dest_s3_uri}")
    except Exception as e:
        print(f"Error copying file in S3: {e}")


def generate_presigned_url(s3_uri: str, expiration: int = 3600) -> str:
    """
    Generate a pre-signed URL to access an S3 object. The URL is valid for the specified expiration time. Default is 1 hour.

    :param s3_uri: S3 URI of the object, e.g. 's3://bucket-name/path/to/file'
    :param expiration: Expiry time in seconds for the pre-signed URL. Default is 3600 seconds (1 hour).
    :return: Pre-signed URL as a string.
    """
    s3_client = boto3.client("s3")
    bucket_name, key = _parse_s3_uri(s3_uri)

    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return ""

    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return ""


def get_latest_ds_nodash(s3_uri: str, skip: int = 0) -> Optional[str]:
    """
    Get the latest ds_nodash (date-stamped folder) from the given S3 URI, with an optional skip count.

    :param s3_uri: S3 URI of the folder, e.g. 's3://bucket-name/path/to/folder/'
    :param skip: The number of most-recent folders to skip. Default is 0.
    :return: The latest ds_nodash string after skipping the specified count, or None if no valid folders are found.
    """
    s3_client = boto3.client("s3")
    bucket_name, prefix = _parse_s3_uri(s3_uri)

    if not bucket_name or not prefix:
        print("Invalid S3 URI.")
        return None

    try:
        # List objects under the given prefix
        response = s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=prefix, Delimiter="/"
        )
        folders = [
            content.get("Prefix").strip("/")
            for content in response.get("CommonPrefixes", [])
        ]

        # Extract date strings and sort them
        date_strings = []
        for folder in folders:
            folder_date_str = folder.split("/")[-1]
            try:
                datetime.strptime(folder_date_str, "%Y%m%d")
                date_strings.append(folder_date_str)
            except ValueError:
                continue  # Ignore folders that do not match the date format

        sorted_dates = sorted(date_strings, reverse=True)

        if skip >= len(sorted_dates):
            print(f"Skip count {skip} exceeds number of available date folders.")
            return None

        return sorted_dates[skip] if sorted_dates else None

    except Exception as e:
        print(f"Error processing S3 folders: {e}")
        return None
